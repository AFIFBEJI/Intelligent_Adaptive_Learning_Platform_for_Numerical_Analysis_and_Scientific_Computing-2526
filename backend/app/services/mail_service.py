# ============================================================
# Mail service: sending emails (verification + reset password)
# ============================================================
# Personalized HTML templates with a nice design (teal header, CTA button,
# Yassine's signature as owner). Plain-text fallback included
# for mail clients that do not support HTML.
#
# Two modes:
#   - "console" (default): log plain-text in uvicorn for the demo
#   - "smtp"             : real multipart send (text + HTML)
# ============================================================
from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage
from pathlib import Path

from app.core.config import get_settings

logger = logging.getLogger(__name__)


# ============================================================
# Founder photo cache (read once at startup)
# ============================================================
# We read the photo from the AUTHOR_PHOTO_PATH path the first time
# an email is sent, then keep the bytes in cache. This avoids
# re-reading the file on every email sent.
_AUTHOR_PHOTO_CACHE: tuple[bytes, str] | None = None  # (bytes, mime_subtype)


def _load_author_photo() -> tuple[bytes, str] | None:
    """Load the founder photo from disk if configured.

    Returns (bytes, mime_subtype) or None if not configured / not found.
    The mime_subtype is deduced from the extension: png -> 'png', jpg/jpeg -> 'jpeg'.
    """
    global _AUTHOR_PHOTO_CACHE
    if _AUTHOR_PHOTO_CACHE is not None:
        return _AUTHOR_PHOTO_CACHE

    settings = get_settings()
    raw_path = settings.AUTHOR_PHOTO_PATH or ""
    # Strip invisible characters (LRM, RLM, BOM) that may linger
    # when copy-pasting a path from Windows Explorer.
    cleaned = "".join(ch for ch in raw_path if ch.isprintable()).strip()
    if not cleaned:
        return None

    p = Path(cleaned)
    if not p.exists() or not p.is_file():
        logger.warning("AUTHOR_PHOTO_PATH=%r introuvable, fallback sur avatar texte.", cleaned)
        return None

    ext = p.suffix.lower().lstrip(".")
    subtype = "jpeg" if ext in ("jpg", "jpeg") else ext  # png, gif, webp...
    if subtype not in ("png", "jpeg", "gif", "webp"):
        logger.warning("Format photo non supporte : %s. Fallback avatar texte.", ext)
        return None

    try:
        data = p.read_bytes()
    except OSError as exc:
        logger.warning("Impossible de lire AUTHOR_PHOTO_PATH=%s : %s", cleaned, exc)
        return None

    _AUTHOR_PHOTO_CACHE = (data, subtype)
    logger.info("Photo fondateur chargee : %s (%d octets, subtype=%s)", cleaned, len(data), subtype)
    return _AUTHOR_PHOTO_CACHE


# ============================================================
# Inline CSS (mail clients ignore <style>, everything must be inlined)
# ============================================================
_BRAND = "#0F766E"
_BRAND_DARK = "#0c5852"
_TEXT = "#1E293B"
_MUTED = "#64748B"
_BG = "#F8FAFC"
_CARD_BG = "#FFFFFF"
_BORDER = "#E2E8F0"


def _html_template(*, headline: str, intro: str, cta_label: str, cta_url: str,
                   sub_message: str, signature_html: str) -> str:
    """Generic responsive HTML email template (600px max, inline CSS).

    All mail clients (Gmail, Outlook, Apple Mail, etc.) support this style.
    """
    return f"""\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{headline}</title>
</head>
<body style="margin:0; padding:0; background:{_BG}; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif; color:{_TEXT};">
  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:{_BG};">
    <tr>
      <td align="center" style="padding:32px 16px;">
        <!-- Card 600px max -->
        <table width="600" cellpadding="0" cellspacing="0" border="0" style="max-width:600px; background:{_CARD_BG}; border-radius:12px; box-shadow:0 4px 20px rgba(15,23,42,0.08); overflow:hidden;">

          <!-- Header avec gradient teal -->
          <tr>
            <td style="background:linear-gradient(135deg, {_BRAND} 0%, {_BRAND_DARK} 100%); padding:36px 40px; text-align:left;">
              <table cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td style="vertical-align:middle;">
                    <div style="background:rgba(255,255,255,0.18); width:48px; height:48px; border-radius:12px; display:inline-block; text-align:center; line-height:48px; color:#ffffff; font-weight:800; font-size:18px; letter-spacing:0.5px;">N</div>
                  </td>
                  <td style="vertical-align:middle; padding-left:14px;">
                    <div style="color:#ffffff; font-size:22px; font-weight:800; letter-spacing:-0.3px;">Numera</div>
                    <div style="color:rgba(255,255,255,0.85); font-size:13px; margin-top:2px;">Adaptive Learning Platform</div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:40px;">
              <h1 style="margin:0 0 20px; font-size:24px; font-weight:800; color:{_TEXT}; line-height:1.3;">{headline}</h1>
              <p style="margin:0 0 24px; font-size:15px; line-height:1.65; color:{_TEXT};">{intro}</p>

              <!-- CTA Button -->
              <table cellpadding="0" cellspacing="0" border="0" style="margin:8px 0 28px;">
                <tr>
                  <td style="background:{_BRAND}; border-radius:8px; box-shadow:0 4px 14px rgba(15,118,110,0.35);">
                    <a href="{cta_url}" style="display:inline-block; padding:14px 32px; color:#ffffff; text-decoration:none; font-size:15px; font-weight:700; letter-spacing:0.2px;">{cta_label}</a>
                  </td>
                </tr>
              </table>

              <p style="margin:0 0 12px; font-size:13px; color:{_MUTED}; line-height:1.6;">{sub_message}</p>

              <!-- Fallback raw URL -->
              <p style="margin:24px 0 0; font-size:12px; color:{_MUTED}; line-height:1.6; word-break:break-all;">
                If the button doesn't work, copy and paste this link into your browser:<br>
                <a href="{cta_url}" style="color:{_BRAND}; text-decoration:underline;">{cta_url}</a>
              </p>

              <!-- Divider + signature -->
              <hr style="border:none; border-top:1px solid {_BORDER}; margin:32px 0;">

              {signature_html}
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:{_BG}; padding:20px 40px; text-align:center; border-top:1px solid {_BORDER};">
              <p style="margin:0; font-size:12px; color:{_MUTED}; line-height:1.5;">
                Numera - Intelligent Adaptive Learning for Numerical Analysis<br>
                You received this email because someone (probably you) signed up on our platform.<br>
                If it wasn't you, you can safely ignore this message.
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""


# Signature personalized by Yassine, in English, with a bit of warmth.
# If a photo is configured (AUTHOR_PHOTO_PATH), we use it via cid:
# (Content-ID, resource embedded in the email). Otherwise text avatar "Y".
def _signature_html() -> str:
    photo = _load_author_photo()
    if photo is not None:
        # Embedded image: we reference it via cid:author_photo. The SMTP
        # sender will add the binary with this Content-ID via add_related().
        avatar_html = (
            '<img src="cid:author_photo" alt="Yassine" '
            'width="64" height="64" '
            'style="display:block; border-radius:50%; object-fit:cover; '
            f'border:3px solid {_BRAND}; box-shadow:0 2px 8px rgba(15,23,42,0.15);" />'
        )
    else:
        avatar_html = (
            f'<div style="background:linear-gradient(135deg, {_BRAND} 0%, {_BRAND_DARK} 100%); '
            'width:64px; height:64px; border-radius:50%; text-align:center; '
            'line-height:64px; color:#ffffff; font-weight:800; font-size:24px;">Y</div>'
        )

    return f"""\
<table cellpadding="0" cellspacing="0" border="0" width="100%">
  <tr>
    <td style="vertical-align:top; width:72px;">
      {avatar_html}
    </td>
    <td style="vertical-align:top; padding-left:16px;">
      <div style="font-size:15px; font-weight:700; color:{_TEXT};">Yassine</div>
      <div style="font-size:12px; color:{_MUTED}; margin-top:2px; letter-spacing:0.3px; text-transform:uppercase; font-weight:600;">Founder & Owner of Numera</div>
      <div style="font-size:13px; color:{_TEXT}; margin-top:12px; line-height:1.6; font-style:italic; padding-left:12px; border-left:3px solid {_BRAND};">
        "Thanks for trying out the platform. If anything feels off or you have ideas to make it better, just reply to this email - I read every message personally."
      </div>
    </td>
  </tr>
</table>
"""


# ============================================================
# VERIFY EMAIL templates (English, personalized)
# ============================================================
def _build_verify_email(name: str, link: str, hours: int) -> tuple[str, str, str]:
    """Returns (subject, plain_text_body, html_body)."""
    display_name = name.strip() if name else "there"
    subject = "Welcome to Numera - Please confirm your email"

    plain = (
        f"Hi {display_name},\n\n"
        f"I'm Yassine, the owner of Numera. Welcome aboard!\n\n"
        f"To activate your account and start your adaptive learning journey, "
        f"please click the link below (valid for {hours}h):\n\n"
        f"{link}\n\n"
        f"If the button doesn't work, copy-paste the URL into your browser.\n\n"
        f"Thanks for trying the platform - if you have any feedback, just reply "
        f"to this email, I read every message personally.\n\n"
        f"--\nYassine\nFounder & Owner of Numera"
    )

    html = _html_template(
        headline=f"Welcome to Numera, {display_name}! 👋",
        intro=(
            "I'm <strong>Yassine</strong>, the owner of this platform. "
            "Thanks for signing up — I'm really glad you're trying it out. "
            "To activate your account and start your adaptive learning journey, "
            "just click the button below."
        ),
        cta_label="Confirm my email",
        cta_url=link,
        sub_message=f"This link is valid for {hours} hours. If you didn't sign up, please ignore this email — no account will be activated.",
        signature_html=_signature_html(),
    )
    return subject, plain, html


# ============================================================
# RESET PASSWORD templates (English, personalized)
# ============================================================
def _build_reset_email(name: str, link: str, hours: int) -> tuple[str, str, str]:
    display_name = name.strip() if name else "there"
    subject = "Reset your Numera password"

    plain = (
        f"Hi {display_name},\n\n"
        f"I'm Yassine, the owner of Numera. We received a request to reset "
        f"your password.\n\n"
        f"If it was you, click the link below to choose a new password "
        f"(valid for {hours}h):\n\n"
        f"{link}\n\n"
        f"If you did NOT request this, you can safely ignore this email — "
        f"your password won't change.\n\n"
        f"Take care,\n--\nYassine\nFounder & Owner of Numera"
    )

    html = _html_template(
        headline=f"Hi {display_name}, let's reset your password 🔐",
        intro=(
            "I'm <strong>Yassine</strong>, the owner of Numera. We received a request "
            "to reset the password for your account. If it was you, click the button "
            "below to choose a new password securely."
        ),
        cta_label="Reset my password",
        cta_url=link,
        sub_message=f"This link is valid for {hours} hour. If you did NOT request this, just ignore this email — your password will stay the same and your account is safe.",
        signature_html=_signature_html(),
    )
    return subject, plain, html


# ============================================================
# Physical sending: console or SMTP
# ============================================================
def _send_console(to_email: str, subject: str, body_plain: str) -> None:
    """Display in the logs (demo mode). We only log the plain-text
    because the HTML would be unreadable in the console."""
    settings = get_settings()
    logger.info("=" * 70)
    logger.info("[MAIL CONSOLE MODE] Email NOT sent (MAIL_MODE=console)")
    logger.info("From   : %s <%s>", settings.MAIL_FROM_NAME, settings.MAIL_FROM)
    logger.info("To     : %s", to_email)
    logger.info("Subject: %s", subject)
    logger.info("-" * 70)
    for line in body_plain.splitlines():
        logger.info(line)
    logger.info("=" * 70)


def _send_smtp(to_email: str, subject: str, body_plain: str, body_html: str) -> None:
    """Real send via SMTP with multipart text + HTML.

    If AUTHOR_PHOTO_PATH is configured, we attach the photo as a related
    resource (Content-ID) so it shows up in the email signature.
    """
    settings = get_settings()
    if not settings.SMTP_HOST:
        logger.warning("MAIL_MODE=smtp mais SMTP_HOST vide ; fallback console.")
        return _send_console(to_email, subject, body_plain)

    msg = EmailMessage()
    msg["From"] = f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    # 1. Plain-text first (legacy clients)
    msg.set_content(body_plain)
    # 2. HTML as an alternative (modern clients)
    msg.add_alternative(body_html, subtype="html")

    # 3. If we have a photo, embed it in the HTML part via cid:
    photo = _load_author_photo()
    if photo is not None:
        photo_bytes, photo_subtype = photo
        # The HTML references cid:author_photo; we add the related
        # resource to the HTML part (the last one added to msg).
        html_part = msg.get_payload()[1]
        html_part.add_related(
            photo_bytes,
            maintype="image",
            subtype=photo_subtype,
            cid="<author_photo>",
        )

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
            if settings.SMTP_TLS:
                server.starttls()
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        logger.info("Email SMTP envoye a %s (subject=%s)", to_email, subject)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Echec envoi SMTP a %s : %s", to_email, exc)


def _dispatch(to_email: str, subject: str, body_plain: str, body_html: str) -> None:
    settings = get_settings()
    mode = (settings.MAIL_MODE or "console").lower()
    if mode == "smtp":
        _send_smtp(to_email, subject, body_plain, body_html)
    else:
        _send_console(to_email, subject, body_plain)


# ============================================================
# Public API
# ============================================================
def send_verification_email(to_email: str, name: str, link: str, language: str = "en") -> None:
    """Signup verification email (English personalized by Yassine).

    The `language` parameter is ignored: we always use English
    for these emails because the platform targets a bilingual audience
    and English is universal. If you want to re-introduce FR later,
    you just need to add a mapping like before.
    """
    _ = language  # to avoid the "unused param" lint
    settings = get_settings()
    subject, plain, html = _build_verify_email(
        name=name,
        link=link,
        hours=settings.EMAIL_VERIFICATION_TOKEN_HOURS,
    )
    _dispatch(to_email, subject, plain, html)


def send_reset_password_email(to_email: str, name: str, link: str, language: str = "en") -> None:
    """Password reset email (English personalized by Yassine)."""
    _ = language
    settings = get_settings()
    subject, plain, html = _build_reset_email(
        name=name,
        link=link,
        hours=settings.EMAIL_RESET_TOKEN_HOURS,
    )
    _dispatch(to_email, subject, plain, html)
