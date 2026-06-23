"""Router serving metadata for the Manim animations attached to concepts.

The animations themselves are pre-rendered MP4 files served as static
assets (mounted in app.main on /static/animations/). This router only
tells the frontend WHICH animation exists for a given concept and what
its URL is, so the SPA can decide whether to render a <video> player
at the top of the content page.

Why a dedicated endpoint instead of just guessing the URL ?
  * Lets us return 404 cleanly when no animation exists yet (most concepts)
  * Avoids hardcoding the static path on the frontend side
  * Future-proof : we can switch to a CDN URL later without changing the SPA
"""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/animations", tags=["animations"])

# Resolve <repo>/backend/static/animations once at import-time.
_STATIC_ANIMATIONS_DIR = Path(__file__).resolve().parents[2] / "static" / "animations"


@router.get("/{concept_id}")
def get_animation_for_concept(concept_id: str, lang: str = "en") -> dict:
    """Return the URL of the Manim animation for a given concept.

    Response shape :
        {
            "concept_id": "concept_lagrange",
            "lang": "en",
            "url": "/static/animations/concept_lagrange_en.mp4",
            "available": true
        }

    If the file does not exist, HTTP 404. The frontend MUST handle 404
    gracefully (just skip the video player) since most concepts will not
    have an animation rendered yet.
    """
    lang_norm = "fr" if lang.lower() == "fr" else "en"
    filename = f"{concept_id}_{lang_norm}.mp4"
    candidate = _STATIC_ANIMATIONS_DIR / filename

    # Fallback : if the localized version is missing, try the English one.
    if not candidate.exists() and lang_norm == "fr":
        fallback = _STATIC_ANIMATIONS_DIR / f"{concept_id}_en.mp4"
        if fallback.exists():
            return {
                "concept_id": concept_id,
                "lang": "en",
                "url": f"/static/animations/{fallback.name}",
                "available": True,
                "fallback_used": True,
            }

    if not candidate.exists():
        raise HTTPException(
            status_code=404,
            detail=f"No animation available for concept '{concept_id}' (lang={lang_norm}).",
        )

    return {
        "concept_id": concept_id,
        "lang": lang_norm,
        "url": f"/static/animations/{filename}",
        "available": True,
    }


@router.get("")
def list_animations() -> dict:
    """List every animation available on disk. Useful for the admin/debug page."""
    if not _STATIC_ANIMATIONS_DIR.exists():
        return {"count": 0, "animations": []}

    items = []
    for f in sorted(_STATIC_ANIMATIONS_DIR.glob("*.mp4")):
        # Filename convention : <concept_id>_<lang>.mp4
        stem = f.stem
        if "_" in stem:
            concept_id, _, lang = stem.rpartition("_")
        else:
            concept_id, lang = stem, "en"
        items.append({
            "concept_id": concept_id,
            "lang": lang,
            "url": f"/static/animations/{f.name}",
            "size_kb": f.stat().st_size // 1024,
        })

    return {"count": len(items), "animations": items}
