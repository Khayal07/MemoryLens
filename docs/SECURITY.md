# Security

MemoryLens went through two pentest-style audits (backend API + frontend/infra) before
deployment. This document records the threat model, what was already solid, what was
hardened, and the known follow-ups.

## Threat model

The primary risk is **cost abuse**: `/search` triggers a paid LLM call, so an
unbounded caller could drain the OpenAI budget. Secondary risks are the usual web app
surface — auth, IDOR, injection, information disclosure, and infra exposure.

## Already solid (verified, not changed)

- **Passwords**: Argon2 (OWASP-preferred, memory-hard).
- **SQL**: SQLAlchemy ORM with parameterized queries throughout; the one raw
  constellation query uses bound parameters. No string-built SQL.
- **Authorization**: user-scoped endpoints (collections, history, constellation,
  sharing) check ownership in the service layer.
- **Prompt injection**: user queries are scrubbed of injection patterns before the LLM
  (`ai/cleaning.py`), and the LLM is constrained to a candidate list — it can't invent
  or act outside it.
- **Share tokens**: `secrets.token_urlsafe(16)` (~128 bits) — unguessable.
- **CORS**: restricted to configured origins, never `*`.
- **Errors**: typed `AppError` → clean JSON envelope; no stack traces leak.
- **Secrets**: `.env` is gitignored and was **never** committed — no key exists in any
  tracked file across the whole git history. Only `.env.example` (placeholders) ships.

## Hardening applied (pre-deploy)

| Area | Fix |
|---|---|
| **Cost abuse (primary)** | `/search` now **requires login**. Rate limiting is identity-aware: `user:<id>` for authenticated calls, `ip:<addr>` (from `X-Forwarded-For`'s first hop) otherwise. Two limits: a per-user **burst** (`SEARCH_RATE_PER_MIN`, 10/min) and a hard per-user **daily quota** (`SEARCH_DAILY_QUOTA`, 50/day). Both fail open if Redis is down. |
| **Feedback IDOR** | A vote only links to a `search_id` the voter owns; a foreign/unknown id is detached (vote still recorded). |
| **Resource exhaustion** | `/items/{id}/similar` `?limit=` capped to 1–50. |
| **Auth integrity** | In production, the API refuses to start unless `JWT_SECRET` is changed from the default (fail-fast validator). |
| **Info disclosure** | In production, `/docs`, `/redoc`, `/openapi.json` are disabled, and `/metrics` requires an `X-Metrics-Token` header. |
| **Browser hardening** | Every response carries `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`, and a conservative CSP; HSTS in production. CORS narrowed to the methods/headers actually used. |
| **Infra** | `docker-compose.prod.yml`: Postgres/Redis unpublished (internal only), Redis password-protected, API without `--reload`, frontend as a built static bundle behind nginx. Backend image runs as a non-root user. |

The rate limiter lives in `app/core/rate_limit.py`; the security headers middleware in
`app/core/middleware.py`; the production toggles in `app/core/config.py` (`is_production`).

## Verified

Live checks confirmed: unauthenticated `/search` → 401; authenticated → 200; the
per-minute limit returns 429 after 10 rapid requests; `?limit=99999999` → 422; security
headers present; `/metrics` open in dev. 188 backend tests pass (including 30 new ones
for rate limiting, feedback ownership, and config validation).

## Known follow-ups (out of scope for this round)

- Move tokens from `localStorage` to httpOnly cookies (mitigates XSS token theft).
- Refresh-token rotation + a logout/revocation blacklist.
- Generic auth error messages (anti-enumeration).

## Deploying safely

See [../README.md](../README.md) → "Deploying to production". In short: set strong
secrets (`openssl rand`), `ENV=production`, use `docker-compose.prod.yml`, and put a
TLS-terminating reverse proxy in front. **Rotate any key that has ever sat in a shared
`.env`.**
