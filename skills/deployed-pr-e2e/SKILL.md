---
name: deployed-pr-e2e
description: >-
  Run a fail-closed authenticated E2E evidence matrix against the live
  staging.plxcustomer.io deploy for a named pack. Use when a human explicitly
  names this skill or asks to run the deployed-PR UAT harness. Scores SOP cases
  plus edge, workflow-loop, speed, and UI/UX rows. Does not auto-start on
  casual readiness questions.
disable-model-invocation: true
---

# Deployed-PR E2E

Staff UAT of a **live** staging deploy. Produce a scored evidence matrix.
Do not write product code, open a PR, or "fix" CI unless a real user-visible
defect blocks a case and a human authorized that fix.

## When to use

Only when a human **names this skill** (or says "run the deployed-PR UAT
harness"). Casual "is this operator-ready?" does **not** start a run.

The human must name the pack(s). If they name none, STOP and ask. If no
pack exists for the surface, draft a pack from the live SOP / module
README and **do not execute it**.

## Fail-closed target

- Host: `https://staging.plxcustomer.io` only. Never production. Never
  `*-git-staging-*.vercel.app`.
- Before any UI work, run `scripts/assert-exact-staging-deploy.mjs`.
  It resolves the alias and **records** SHA, `dpl_`, and timestamp.
  If a human pinned SHA/`dpl`, prove a match or STOP.
- Live app reads `plx-postgres-uat`. Confirm required migrations; do not
  re-apply them.
- Login: agent STAFF via `plx-portal-agent-access` (real NextAuth). No
  auth bypass. Never print credentials.
- Browser: `autobrowse` + cursor-ide-browser (list tabs, navigate, lock,
  snapshot, act by refs). Fresh snapshot after every navigation/click.
  Stop after 4 failed attempts on the same control.

## Reuse (do not fork)

| Job | Skill / rule |
|---|---|
| STAFF login | `plx-portal-agent-access` |
| Browser path | `autobrowse` |
| Vendor/ops mail | `plx-graph-mail` + `email-theme` |
| Operator retest gate | `e2e-before-operator-retest` |
| Independent verify | [references/independent-verify.md](references/independent-verify.md) |

Persona QA / post-deploy smoke / page-marker smoke are **not** a
substitute for this matrix.

## Packs

Read [references/pack-schema.md](references/pack-schema.md). Load only
the named pack file under `packs/`.

- SOP / module README wins for existing test IDs. Drift is a **pack
  defect**, not a product FAIL. Do not invent cases.
- Every pack must declare happy-path IDs and the five dimension row
  sets: use-cases, edge-cases, workflow-loop E2E, speed, UI/UX.
- Speed rows name a class from [references/SPEED-BUDGET.md](references/SPEED-BUDGET.md).
- Viewport rows follow [references/UX-VIEWPORT.md](references/UX-VIEWPORT.md).
  If the named PR stamps `Surface-change: yes`, incorporate UX-VP-* at
  the listed surfaces. Do not infer a surface change from SOP prose.
- API rows follow [references/API-CONTRACT.md](references/API-CONTRACT.md).
  `Api-change: yes` incorporates API-AUTH / API-CONTRACT / API-ERROR.
  Latency reuses the speed classes.
- Security rows follow [references/SECURITY.md](references/SECURITY.md).
  `Security-change: yes` incorporates SEC-HOST / AUTHN / AUTHZ /
  SECRETS / ISOLATION. Defensive checks only. No exploit steps.
- Maturity map: [references/MATURITY.md](references/MATURITY.md).
- First pack: [packs/bom-comms.md](packs/bom-comms.md) (UAT-SOP §81).

## Run loop

```text
Deployed-PR E2E
- [ ] 1. Human named this skill and at least one pack
- [ ] 1b. If a PR number is named, parse harness stamps
         (parse-surface-change.mjs --pr N). Missing Surface-change = STOP
- [ ] 2. Alias proof recorded (SHA + dpl + timestamp)
- [ ] 3. STAFF session via plx-portal-agent-access
- [ ] 4. Pick a mutable sandbox / UAT-prefixed fixture; record it
- [ ] 5. Execute every pack case, then every dimension row
- [ ] 5b. If Surface-change: yes, prove UX-VP-* at listed surfaces
- [ ] 5c. If Api-change: yes, prove API-AUTH / CONTRACT / ERROR
- [ ] 5d. If Security-change: yes, prove SEC-* (defensive only)
- [ ] 6. Score PASS / FAIL / BLOCKED with URL + evidence
- [ ] 7. Write RESULTS.md + RESULTS.json (include surfaceChange,
         apiChange, securityChange)
- [ ] 8. validate-results.mjs exits 0
- [ ] 9. Fresh subagent independent-verify score > 8
- [ ] 10. Verdict: operator-ready or not
```

Do not mark PASS without a screenshot path or API proof. Do not ask
Vince to retest until the pack-declared happy path is PASS or honest
BLOCKED and step 9 passed.

## Scoring

| Result | Meaning |
|---|---|
| PASS | Observed expected behavior; proof attached |
| FAIL | Expected behavior missing; proof attached |
| BLOCKED | Could not execute (fixture, NAA, permission); say why |

operator-ready only if every happy-path ID and every required dimension
row is PASS or honest BLOCKED, `validate-results.mjs` exits 0, and
independent-verify score is greater than 8. Any FAIL on those rows
means **not operator-ready**.

## Kill bar (fail the skill, not a weak draft)

- Agents invent cases or skip deploy-proof and still mark operator-ready
- A run tests the lagging git alias, production, or emails a real vendor
- The pack freezes a dated prompt and drifts from the live SOP
- A named PR is missing `Surface-change:` and the run still marks
  operator-ready
- `Surface-change: yes` and the run skips UX-VP-* rows
- `Api-change: yes` and the run skips API-* rows
- `Security-change: yes` and the run skips SEC-* rows
- The run writes an exploit, payload, or attack procedure

## Out of scope

- Product code, production, `master`, Vercel alias changes
- Compliance workflow edits
- Real customer/vendor email (internal-only / draft / mock)
- MIME / HTML / message body posted to a PLX API
- Replacing `uat-runner`, weekly UAT loop, or Playwright CI

## Scripts

```bash
node scripts/assert-exact-staging-deploy.mjs
node scripts/assert-exact-staging-deploy.mjs --require-sha <40hex> --require-dpl dpl_...
node scripts/validate-results.mjs --selftest
node scripts/validate-results.mjs path/to/RESULTS.json --pack packs/bom-comms.md
node scripts/parse-surface-change.mjs --selftest
node scripts/parse-surface-change.mjs --pr 676
```

## Additional resources

- Pack schema: [references/pack-schema.md](references/pack-schema.md)
- Speed budget: [references/SPEED-BUDGET.md](references/SPEED-BUDGET.md)
- UX viewport / PR stamp: [references/UX-VIEWPORT.md](references/UX-VIEWPORT.md)
- API contract: [references/API-CONTRACT.md](references/API-CONTRACT.md)
- Security: [references/SECURITY.md](references/SECURITY.md)
- Maturity map: [references/MATURITY.md](references/MATURITY.md)
- Independent verify: [references/independent-verify.md](references/independent-verify.md)
- RESULTS templates: [examples/RESULTS.template.md](examples/RESULTS.template.md)
- Harness detail: [reference.md](reference.md)
