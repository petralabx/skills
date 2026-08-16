# Deployed-PR E2E — maturity map

What this skill owns, what is a candidate, and what stays out.
Do not invent a class that is not on this list.

## Adopted (company standard)

| Area | File | How a PR turns it on |
|---|---|---|
| Speed | [SPEED-BUDGET.md](SPEED-BUDGET.md) | Always, when the pack has SP rows |
| Viewport / responsive | [UX-VIEWPORT.md](UX-VIEWPORT.md) | `Surface-change: yes` |
| API Auth / Contract / Error | [API-CONTRACT.md](API-CONTRACT.md) | `Api-change: yes` |
| Security Host / Authn / Authz / Secrets / Isolation | [SECURITY.md](SECURITY.md) | `Security-change: yes` |
| SOP cases + five dimensions | [pack-schema.md](pack-schema.md) | Named pack |
| Independent verify | [independent-verify.md](independent-verify.md) | Every run |

## Candidate (named, not gated)

| Area | Why it is not gated yet |
|---|---|
| Speed Chrome (300 ms) | No Close-ticket / Recents timing |
| Touch 44 px | WCAG AA floor is 24 px; 44 is a goal |
| CSRF | No measured reject run |
| XSS escape on proved surface | Needs a fixture string, not a payload cookbook |
| Axe serious/critical on pack surfaces | ui-gate has it; this skill does not call it yet |
| Staff MRP mobile-required | Product call still open |
| Production p75 SLO | Different harness (telemetry), same class names |

## Out of this skill (on purpose)

| Area | Where it lives |
|---|---|
| Load / concurrency | k6 / perf-budget-loop, not UAT |
| Browser matrix beyond Chromium | Not staffed |
| Email / MIME / vendor send | `plx-graph-mail` + email-theme |
| Mission Control Ask | Wrong host |
| Prisma vs FM schema | Repo `.cursorrules`, not this matrix |
| MC checkout / compliance | `plx-mc-compliance` CI |
| Silent-failure audit | Advisory CI |
| Dual-DB migrate | `staging-dual-db-migrate` |
| Voice Path A/B | SOP N/A unless mic granted |
| i18n / SEO / print / offline | Not a PLX staff UAT claim |

## Still missing for frontier (do not pretend we have these)

1. **Promote this skill to `petralabx/skills`** so every agent sees the tables.
2. **Wire ui-gate axe** into the viewport pass when `Surface-change: yes`.
3. **Isolation fixture** (second UAT customer id) so SEC-ISOLATION can PASS.
4. **Keyboard / focus** on Confirm, Close, and COS composer (a11y beyond axe).
5. **Two-tab write** (idempotent close / double Send) — not a load test.
6. **PII in screenshots** (redact customer names in evidence).
7. **Feature-flag matrix** (voice off is N/A; do not FAIL).
8. **Time / timezone** on ticket timestamps (one row, when a pack cares).

A mature run names every adopted class that the PR stamp turned on,
and leaves candidates BLOCKED with the reason above. It does not
invent a ninth class in the pack.
