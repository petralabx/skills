# Portal PR template — harness stamps

Paste this block into
`.github/PULL_REQUEST_TEMPLATE.md` after `## Test plan`.
The deployed-pr-e2e skill greps these exact keys.

```markdown
## Surface change

<!-- Required on every PR. The deployed-pr-e2e skill reads these stamps.
     Do not leave Surface-change off a named PR.
     Keys must stay: Surface-change / Surfaces / Viewports /
     Api-change / APIs / Security-change -->

- Surface-change: no
- Surfaces:
- Viewports: desktop, tablet, mobile
- Api-change: no
- APIs:
- Security-change: no
```

Labels (same meaning as `yes`): `surface-change`, `api-change`,
`security-change`.
