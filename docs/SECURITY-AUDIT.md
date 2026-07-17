# Security Audit — 2026-07-17

A pentester-style re-audit of MemoryLens before the university demo. Combines a
**static** pass (reading the auth, authorization, injection, rate-limit, secrets and
header code) with a **dynamic** pass (real HTTP probes against the live localhost
stack). This complements [SECURITY.md](SECURITY.md), which records the threat model and
the pre-deploy hardening; this file is the dated verification that those controls still
hold.

**Result: no vulnerabilities found.** Every control tested behaved as designed.

## Scope & method

- **Static**: `app/core/security.py`, `config.py`, `middleware.py`, `rate_limit.py`,
  `errors.py`, `api/deps.py`, all `api/v1/*` routers, and the IDOR-relevant services
  (`collections_service`, `feedback_service`, `share_service`, `constellation_service`).
- **Dynamic**: `curl` probes against `http://localhost:8000` with the stack up
  (`docker compose up`), using two fresh accounts (user A / user B) plus a throwaway
  account for the rate-limit burst.
- **Secrets**: `git ls-files` + `git grep` over tracked content for key patterns.

## Findings by class

| Class | Verdict | Evidence |
|-------|---------|----------|
| **AuthN** | PASS | Argon2 hashing (`security.py`). Dual JWT (access 15m / refresh 7d), HS256. `config.py` `_require_strong_secret_in_prod` fails startup if `JWT_SECRET` is default/blank outside dev. |
| **Token abuse** | PASS | Forged-signature token → 401. Refresh token replayed as access token → 401 (`deps.py` `payload.get("type") != "access"`). |
| **AuthZ / IDOR** | PASS | User B cannot read, rename, delete, or add-item to user A's collection (all 404 via `collections_service._owned`); cannot share A's search (404, `share_service`); cannot list A's history. B's vote carrying A's `search_id` returns 204 but the search link is **silently detached** (`feedback_service.record_vote`). |
| **Injection (SQL)** | PASS | All queries ORM-parameterized. The single raw query (`constellation_service._similarity_edges`) uses `text()` with bound `:ids`/`:min_sim` params — no string interpolation. |
| **Injection (prompt)** | PASS | Queries scrubbed in `ai/cleaning.py`; LLM constrained to a candidate list (grounded RAG). |
| **Cost abuse / DoS** | PASS | `/search` requires auth + per-user `user_rate_limiter` (10/min) + `daily_quota` (50/day). Burst test: 10× 200 then 429. Limiters fail-open behind a circuit breaker if Redis is down. |
| **Input caps** | PASS | `/items/{id}/similar?limit=99999` and `?limit=-1` → 422 (`Query(6, ge=1, le=50)`). Invalid `vote` value → 422. |
| **Admin surface** | PASS | `ADMIN_TOKEN` blank in dev ⇒ whole `/admin/*` surface returns 404 (fail-closed, `require_admin`). Wrong token also 404 while blank; 401 only once a token is set. |
| **Share tokens** | PASS | `secrets.token_urlsafe(16)` (~128 bits). Garbage token → 404 with no enumeration signal. |
| **Info disclosure** | PASS | Generic error envelope (`errors.py`), no stack traces. Bad login → "Invalid email or password." (no user enumeration). `/docs`, `/redoc`, `/openapi.json` hidden in prod; `/metrics` gated by `X-Metrics-Token` in prod (open in dev by design). |
| **Security headers** | PASS | Every response carries `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`, a restrictive CSP, and `X-Request-ID`. HSTS emitted in prod only. |
| **CORS** | PASS | Origin allowlist from `CORS_ORIGINS` (never `*`); methods limited to GET/POST/OPTIONS; named headers only. |
| **Secrets in repo** | PASS | No tracked `.env`/`*.key`/`*.pem`; `.env` and `backend/.env` gitignored; `git grep` for `sk-…`/`AKIA…`/PEM patterns over tracked files = no matches. Only `.env.example` placeholders ship. |

## Dynamic probe log (abridged)

```
unauth POST /search                         -> 401
admin/catalog/stats (no token)              -> 404
admin/ingest (wrong token)                  -> 404
items/1/similar?limit=99999 | ?limit=-1     -> 422 | 422
share/<garbage>                             -> 404
security headers on /health                 -> all present
/metrics (dev)                              -> 200 (gated in prod)
register weak pw (<8) | duplicate email     -> 422 | 409
userB rename/delete/add A's collection      -> 404 / 404 / 404  (A's collection intact)
userB share A's search 349                  -> 404
userB vote w/ A's search_id                 -> 204 (link detached; B history = 0)
invalid vote value                          -> 422
forged JWT | refresh-as-access              -> 401 | 401
rate-limit burst (12x)                      -> 200×10, 429×2
```

## Recommendations (unchanged from SECURITY.md — not vulnerabilities)

These are hardening opportunities, not defects; deferred by design for this project's
scope:

1. **Token storage**: access/refresh tokens live in `localStorage` (XSS-readable).
   Moving to httpOnly, `SameSite=Strict` cookies would neutralize token theft via XSS.
2. **Refresh-token rotation + revocation**: refresh tokens are stateless and long-lived
   (7d); there is no logout/blacklist. Rotation + a server-side denylist would allow
   real revocation.
3. **`X-Forwarded-For` trust**: the IP-keyed limiter reads the first XFF hop; only run
   behind a proxy that overwrites XFF, or a client can spoof its bucket. (Already noted
   in `rate_limit.py`.)

## Housekeeping (found during audit)

- `app/api/deps.py:get_optional_user` is defined but never imported — dead code, removed
  in the code-review cleanup pass (harmless; search is auth-only now).
