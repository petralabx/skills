# Independent verify

After the runner writes RESULTS.md / RESULTS.json, a **fresh** subagent
re-reads the matrix. The runner must not self-score this pass.

## Prompt (give to a new Task / subagent)

```text
You are the independent verifier for a deployed-pr-e2e run.
Read-only. Do not log in as a different story. Do not change RESULTS.

1. Read RESULTS.md, RESULTS.json, and proof.json.
2. Confirm proof.host is https://staging.plxcustomer.io and SHA/dpl are present.
3. Sample at least 5 PASS rows: open the named evidence file or API proof.
   Fail the score if a PASS has no readable proof.
4. Confirm happy-path IDs from the pack are PASS or honest BLOCKED.
5. Confirm the five dimension sections have rows.
6. Confirm operator-ready is not claimed if any happy-path or required
   dimension row is FAIL.
7. If RESULTS.surfaceChange.declared is true, confirm UX-VP-* rows
   exist for each required viewport and have readable screenshots.
8. If RESULTS.apiChange.declared is true, confirm API-AUTH,
   API-CONTRACT, and API-ERROR have readable httpProof.
9. If RESULTS.securityChange.declared is true, confirm SEC-* rows
   exist. Isolation may be honest BLOCKED. Fail if evidence looks
   like an exploit or a secret.

Return exactly:
INDEPENDENT_VERIFY: score=<1-10> pass=YES|NO
Then 5-10 lines of evidence. pass=YES only if score > 8.
```

Prefer a different model family than the runner (spec critic role).
`pass: YES` only if `score > 8`. Same pattern as `uat-loop-invariants` IV.
