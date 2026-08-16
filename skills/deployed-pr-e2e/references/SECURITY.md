# Company security gate

Canonical for every `deployed-pr-e2e` pack. These are **defensive**
checks. Do not write exploits, payloads, or attack procedures.

Adopted 2026-08-16.

## Classes

| Class | Gate | Status |
|---|---|---|
| Host | proof.host is `https://staging.plxcustomer.io`. Never production. Never the lagging git alias | Adopted (already in validate-results) |
| Authn | Staff API or staff page without a session is 401 / login, not 200 with data | Adopted |
| Authz | STAFF cannot complete an ADMIN-only action. CUSTOMER cannot open `/admin/*` | Adopted |
| Secrets | RESULTS, screenshots, and chat contain no password, token, or connection string | Adopted |
| Isolation | STAFF cannot read another customer's record. Expect 403/404, not 200 with that row | Adopted when a second-customer fixture exists; else BLOCKED `no isolation fixture` |
| CSRF | Cookie mutation without the NextAuth CSRF token is rejected | Candidate. Do not FAIL until one measured run exists |
| XSS | Staff-controlled HTML is escaped. No unsanitized `dangerouslySetInnerHTML` on the proved surface | Candidate |

## PR stamp

```text
- Security-change: yes
```

Use `yes` when the PR touches auth, RBAC, cookies, sessions, or
customer scoping. `no` otherwise. Missing stamp on a named PR is a STOP.

Optional label: `security-change`.

## Required rows when `Security-change: yes`

| ID | Class |
|---|---|
| SEC-HOST | Host class (cite proof.json) |
| SEC-AUTHN | Authn on one listed staff API or page |
| SEC-AUTHZ | Authz: STAFF denied on one ADMIN path, or CUSTOMER denied on `/admin` |
| SEC-SECRETS | Evidence files have no secret (scan notes + httpProof for `password=`, `Bearer `, `postgresql://`) |
| SEC-ISOLATION | Isolation, or honest BLOCKED `no isolation fixture` |

Do not probe production. Do not use a real customer flagship as the
foreign row. Use a UAT-prefixed sandbox id.
