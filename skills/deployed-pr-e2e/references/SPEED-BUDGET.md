# Company speed budget

Canonical for every `deployed-pr-e2e` pack. Packs name a **class**.
They do not invent a sixth number.

Adopted 2026-08-16. Chrome stays a candidate until one Close-ticket or
Recents run exists.

## Gate

| Rule | Value |
|---|---|
| Host | `https://staging.plxcustomer.io` only |
| Actor | STAFF, desktop, page already open |
| Warmup | 1 discarded run, then 5 timed runs |
| Statistic | **max of those 5 warm runs** (do not call this p95) |
| Cold | Record it. Do not gate on it. |
| Fail | Over budget, or any non-200 in the five, is FAIL |
| Kind | Single-user UAT gate. Not a load test. |
| Proof | Record the deploy SHA next to the timings |

Later production telemetry may use the same classes and numbers at
p75 of live traffic. That SLO is not this harness.

## Classes

| Class | Clock | UAT gate | Status |
|---|---|---|---|
| Chrome | Button or panel to first visible change | 300 ms | **Candidate.** Score BLOCKED with reason `chrome budget is candidate`. Do not FAIL. |
| Fetch | Click or GET to a known body on screen | 1000 ms | Adopted |
| Stream | Send to first SSE `delta` frame | 2000 ms | Adopted |
| Write | Save or close to persisted confirmation | 2000 ms | Adopted |
| Page | Navigation to page usable | 3000 ms | Adopted |

Do not budget full COS reply or full Hub search. Those wander.

Empty, heartbeat, or `tool-call` frames do not satisfy Stream. The
clock stops on the first parsed `data:` frame with `type=delta`.

## Clock

Preferred clock is the user-visible change.

An API stand-in is allowed only when the pack says so. A fast GET
does not PASS a slow paint. If the pack uses an API clock, say that
in the Speed row and still require the UI path to be correct on the
matching case (for example KH-11).

## How a pack declares speed

Each Speed row lists `id`, short metric, and **class**. Example:

```text
| SP-01 | COS typed Send to first SSE delta | Stream |
| SP-02 | Hub Ask click to The page body | Fetch |
```

Allowed BLOCKED reasons for speed:

- `chrome budget is candidate`
- `no class fits` — rare; stop and ask. Do not invent a number.
- fixture / NAA / permission, same as any other row

`no budget declared` is no longer valid once a class fits.

## Mapping for current packs

| Pack | Row | Class |
|---|---|---|
| cos-p3-retrieve | SP-01 first SSE delta | Stream |
| cos-p3-retrieve | SP-02 The page body | Fetch |
| cos-close-ticket | SP-01 Close ticket round trip | Write |
| cos-close-ticket | SP-02 Recents refresh shows Closed | Chrome (candidate) |
| bom-comms | SP-01 BOM editor interactive after open | Page |
| bom-comms | SP-02 Sourcing detail save-brief | Write |
