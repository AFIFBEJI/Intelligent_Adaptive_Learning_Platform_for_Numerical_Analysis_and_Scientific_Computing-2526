"""Centralized rate-limiting for the sensitive endpoints.

Why?
====
Without rate-limit, three families of attacks are trivial:

1. **Brute-force login**: `/auth/login` accepts 1000 attempts/second on the
   same account. An attacker can test a dictionary of passwords.

2. **Exhausted OpenAI budget**: `/tutor/sessions/{id}/ask` and
   `/quiz-ai/generate` call the OpenAI API on each request. A user
   (or a bot) can send 1000 questions in 30 seconds and blow up
   the bill in demo mode. With gpt-4o-mini at ~$0.15/M tokens, it is
   theoretically on the order of a few dollars, but on a Free Tier quota
   we block the whole project in a few minutes.

3. **Email spam**: `/auth/forgot-password` and `/auth/request-verification`
   trigger an SMTP send. Without a limit, one can harass any
   email address (and get our Gmail relay blacklisted).

Strategy
========
We use `slowapi`, a modern fork of Flask-Limiter for ASGI/FastAPI.
- Backend: in-memory (sufficient for a single FastAPI backend instance).
  For a multi-replica deployment we will need to switch to Redis:
  `Limiter(storage_uri="redis://...")`.
- Key: client IP (`get_remote_address`). Standard behavior;
  an authenticated user could have a "user_id" key but for
  non-authenticated endpoints (`/auth/login`) the IP is the natural choice.

Quotas
======
Deliberately generous so as not to break the E2E tests nor the demo, but
sufficient to block attacks:

  AUTH_LOGIN          10/minute  (a human does not try 10 passwords/min)
  AUTH_EMAIL          3/minute   (one transactional email per 20s is enough)
  LLM_HEAVY           20/minute  (max ~$0.10/min on gpt-4o-mini)
  LLM_LIGHT           60/minute  (static quizzes, cheap)

If you see these quotas being exceeded during the user study in prod,
increase them here rather than removing the decorator.
"""
from __future__ import annotations

import os

from slowapi import Limiter
from slowapi.util import get_remote_address

# ============================================================
# Conditional activation of rate-limiting
# ============================================================
# In production: active (brute-force defense + OpenAI budget).
# In pytest tests: we disable it so as not to saturate the quota after 10
# tests that hit /auth/login. The TestClient always uses the same fictitious
# IP "testclient", so ALL the tests share the same bucket.
#
# To disable, set in the shell or .env:
#     RATE_LIMIT_ENABLED=false
#
# The tests' conftest.py sets this env var before importing the app.
_enabled = os.environ.get("RATE_LIMIT_ENABLED", "true").lower() != "false"

# Singleton: a single Limiter for the whole app, importable from each router.
# default_limits=[]: no default limit on undecorated routes,
# we opt-in explicitly on the endpoints that need it.
limiter = Limiter(key_func=get_remote_address, default_limits=[], enabled=_enabled)

# Quotas exported as constants to stay DRY and ease the audit.
AUTH_LOGIN_LIMIT = "10/minute"
AUTH_EMAIL_LIMIT = "3/minute"
LLM_HEAVY_LIMIT = "20/minute"
LLM_LIGHT_LIMIT = "60/minute"
