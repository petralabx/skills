---
name: plx-brand
description: >-
  The PLX / Petra Lab-X brand standard — colour tokens, type stacks, logo usage,
  table design, email signature structure, and the chassis-and-folio document
  vocabulary. Use whenever producing anything that carries the PLX name in any
  format: Word documents, Excel workbooks, PowerPoint decks, PDFs, letterheads,
  agreements, proposals, quotes, reports, emails, microsites, or UI. Also use
  when asked for "our brand colours", "the design system", "PLX letterhead", or
  to put something "on brand". Carries every value inline so it works on
  surfaces with no checkout of this repository.
---

<!-- plx-brand-generated
generated-by: scripts/generate-plx-brand-skill.py
package: plx-design-system
version: 1.3.0
integrity: sha256-ce22ba82ba5005ac57d9104e92e9551567b8013ccb96c916fdaca71f34db3d61
tokens_sha256: 19774f70b4073ffa72e813a8e06c14cea4c0b6ad18ba5dbf73a6161d0e2cfd0a
manifest_sha256: cd2b191f597e65b793556d9cc893875fb577da874045ed1882cdde155c75d8ee
-->

# PLX Brand Standard

**Authority:** this repository → `design-system/` (ADR-005)
**Pinned to:** `plx-design-system` v1.3.0 (read `channel` from `design-system/manifest.json`)
**Integrity:** `sha256-ce22ba82ba5005ac57d9104e92e9551567b8013ccb96c916fdaca71f34db3d61`
**tokens.css sha256:** `19774f70b4073ffa72e813a8e06c14cea4c0b6ad18ba5dbf73a6161d0e2cfd0a`
**Brand name:** **Petra Lab-X** (hyphenated) · short form **PLX**
**Descriptor:** *Frontier lab for breakthrough products at scale*

This file is **generated** by `scripts/generate-plx-brand-skill.py` from `design-system/tokens.css`
and `design-system/manifest.json`. Do not edit values by hand. If
`manifest.json` version or integrity changes, re-run the generator.

> **If you have repo access, prefer the source.** Read `design-system/tokens.css`
> and `design-system/manifest.json` directly. Treat this skill as stale if the
> pin above does not match those files.

---

## Read this first

**1. ADR-001 is out of date.** `docs/design-system/decisions/ADR-001-brand-vocabulary.md`
is v0.2 (May 2026) and still names rust and Geist as live values. Keep ADR-001
for its *reasoning*, never its values. `#244A39` (`--p-accent`) and
`Inter` (`--p-font-sans`) come from `tokens.css`. Do not copy ADR-001 hex or
faces into new work.

**2. Never invent a value.** No approximated hex, no guessed legal entity name,
no invented address or phone number, no substitute logo mark. If something you
need is missing, produce the work with a clearly marked placeholder and say what
you need. See **What this skill cannot give you**.

---

## Colour

Token values below are copied from `:root` in `tokens.css`. Hairline flats and
status soft tints are **derived** (alpha flattened onto `--p-paper`, or a 12%
mix of the status fill on `--p-paper`) so Office and email clients that cannot
carry `rgba()` still have a number that traces to the authority file.

### Light scheme (the default)

| Token | Value | Role |
|---|---|---|
| `--p-paper` | `#FBFAF6` | Page and cards — the primary surface |
| `--p-paper-2` | `#ECEFE9` | Recess: rails, footers, hovers, table headers |
| `--p-rail` | `#EEEBE3` | Global rail, inner sidebar, label bands |
| `--p-canvas` | `#F5F3EC` | Page ground beneath cards on dense surfaces |
| `--p-ink` | `#1B1A17` | Primary text, headings |
| `--p-ink-2` | `#3A3833` | Secondary text, body copy |
| `--p-muted` | `#6B665B` | Tertiary text, mono labels |
| `--p-accent` | `#244A39` | Primary action, active state, the one flourish |
| `--p-accent-soft` | `#BCCFBF` | Accent tints and backgrounds |
| `--p-grid` | `rgba(27, 26, 23, 0.16)` → flat `#D7D6D2` | Hairline rules |
| `--p-grid-2` | `rgba(27, 26, 23, 0.08)` → flat `#E9E8E4` | Fainter hairline |

Use the derived flat hex for hairlines wherever alpha is awkward (email, Office).

### Status — earth tones, never alarm colours

| Token | Fill | Text shade | Soft tint (12% on paper) | Means |
|---|---|---|---|---|
| `--p-ok` | `#5C7A55` | `#48603F` | `#E8EBE3` | Approved · live · signed |
| `--p-warn` | `#C99340` | `#7E5C0F` | `#F5EEE0` | Pending · in review · open flag |
| `--p-info` | `#5B7B91` | `#476378` | `#E8EBEA` | Informational |
| `--p-hot` | `#52606E` | `#46535F` | `#E7E8E6` | **Destructive only** — not "needs review" |

Use the **text** shade for type, the base for chip fills, the soft tint for
boxes and rules. Soft tints tint **boxes only** — never a full-width band.

### Dark scheme

`--p-paper` `#1A1816` · `--p-paper-2` `#22201D` ·
`--p-rail` `#16140F` · `--p-ink` `#F1ECE0` ·
`--p-ink-2` `#C9C2B5` · `--p-muted` `#A09789` ·
`--p-accent` `#7AB18C` · `--p-accent-soft` `#264132` ·
`--p-ok` `#7EA372` · `--p-warn` `#D9A85C` ·
`--p-info` `#7A9DB3` · `--p-hot` `#8FA0B0`

Do not hand-tune dark values. They live in the `.dark` block of `tokens.css`.

---

## Type

Three stacks, three jobs. Faces are parsed from `--p-font-*` in `tokens.css`.

| Stack | Face | Fallbacks in the token | Job |
|---|---|---|---|
| serif | **Mazius Display** | `var(--font-mazius-display, "Mazius Display"), "Times New Roman", Georgia, serif` | Heroes, deed and agreement titles, thresholds |
| sans | **Inter** | `var(--font-inter, "Inter"), "Segoe UI", "Helvetica Neue", Arial, sans-serif` | Body, labels, tables, navigation |
| mono | **JetBrains Mono** | `var(--font-jetbrains-mono, "JetBrains Mono"), "IBM Plex Mono", ui-monospace, monospace` | Data, IDs, timestamps, kickers, metadata |

Mazius Display ships under the SIL Open Font License. **Only the 400 regular and
400 italic cuts are licensed for use** — bold and extra-italic cuts exist in the
archive but must not be used. It is a **display** face: never set body copy in
it, and never run body text in mono.

**Where webfonts cannot be relied on** — email, and any file opened on a machine
that may not have the fonts installed — drop to the documented safe stacks
rather than shipping a broken render:

- serif → `Georgia, 'Times New Roman', serif`
- sans → `'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif`
- mono → `'JetBrains Mono', 'IBM Plex Mono', Menlo, Consolas, ui-monospace, monospace`

### Scale (screen, from `--p-text-*`)

display `56` · h1 `32` ·
h2 `24` · h3 `18` ·
body `14` · body-compact `13` ·
small `12` · mono `11` ·
meta `10` · kicker `9.5` ·
tick `9`

### Tracking — the signature move

Small mono labels, uppercase, generously letter-spaced (`--p-track-*`):

- kicker / ticks — `0.22em`
- metadata — `0.16em`
- data — `0.04em`

This reads as instrumentation: a label on a panel, not a UI string. It is the
most recognisable thing about the brand. Use it for running heads, reference
lines, table headers, and section kickers.

### The rationed italic

**One** italic accent word inside a serif headline. Never more. When
`--p-accent` appears, it means something.

---

## Logo

Six PNGs live in `docs/design-system/assets/logos/` (three layouts × two
treatments), all on transparent ground. Dimensions below were read from the
files at generate time.

| File | Layout | Treatment | Use for |
|---|---|---|---|
| `logo-full-cream.png` | Full lock-up | Cream | Dark backgrounds, photography overlays |
| `logo-full-ink.png` | Full lock-up | Ink | Light backgrounds — the primary choice |
| `logo-horizontal-cream.png` | Horizontal | Cream | Headers on dark |
| `logo-horizontal-ink.png` | Horizontal | Ink | Headers, letterheads, narrow horizontal space |
| `logo-stacked-cream.png` | Stacked | Cream | Square spaces on dark |
| `logo-stacked-ink.png` | Stacked | Ink | Square spaces, social avatars |

Plus `mark-ink-128.png` — the periodic-mark glyph, for places that cannot render
the full lock-up (favicons, avatars, a slide corner).

**What the marks actually are.** Periodic-element mark: paper square with `14`
top-left and italic serif `Px` bottom-right (Petra Lab-X → Px). Wordmark:
"Petra Lab-X." italic Mazius with `-X` in forest. Ink on paper, cream on dark.

**SVG versions exist in the Claude Design project** (`assets/logo-mark.svg`,
`assets/logo-horizontal-{ink,cream}.svg`) but are not vendored into this repo.

### Vector source — use this for print

There **is** a true vector master in the repo:

```
docs/design-system/assets/logos/PLX_LOGO_VECTOR.pdf
```

Original handoff filing (same bytes): `docs/design-system/specs/_handoff-context/reference-images/logo_file-1777802508146.pdf`

Verified vector: no embedded rasters, no font dependencies (type is outlined),
two artboards — horizontal at 408.5 × 106.8 pt and stacked at 215.5 × 232.2 pt.
It scales to any size.

Inspected at generate time: title `PLX_LOGO_VECTOR`, creator `Adobe Illustrator 27.3`,
3 pages, 357478 bytes (≈ 349 KB), created 2024-10-09.

**The PNGs are 1× rasterizations of that PDF**, which is why their pixel
dimensions match its artboards exactly:

| File | Pixels | Clean print width @300 DPI |
|---|---|---|
| Full lock-up | 475 × 231 | ≈ 1.58 in / 40 mm |
| Horizontal | 409 × 107 | ≈ 1.36 in / 35 mm |
| Stacked | 216 × 233 | ≈ 0.72 in / 18 mm |

So the PNGs are fine for screen and for small print marks at those sizes. For
**anything larger — a deck title slide, a letterhead banner, signage — place the
PDF, or export SVG/PNG from it at the size you need.** Never upscale a PNG when
the vector master is right there.

Duplicate raw exports of the same three lock-ups also sit beside the handoff
PDF as `logo-p1.png` (horizontal), `logo-p2.png` (stacked) and `logo-p3.png`
(full). Prefer the named files in `docs/design-system/assets/logos/`.

Favicons and the runtime lock-up subset are in `portal/public/brand/`
(populated): `favicon-16.png`, `favicon-180.png`, `favicon-32.png`, `favicon-512.png`, `favicon-64.png`, `favicon-dark.svg`, `favicon.svg`, `logo-full-cream.png`, `logo-full-ink.png`, `logo-horizontal-cream.png`, `logo-horizontal-ink.png`, `logo-stacked-ink.png`, `mark-ink-128.png`.

### Usage

- Give the lock-up clear space on all sides of at least the height of its mark.
  *(Working default — not a documented brand rule. Confirm with Vince if a
  formal exclusion zone matters for a given piece.)*
- Ink on light, cream on dark. Never ink on a dark ground.
- Never recolour it, stretch it, add effects, rotate it, or place it on a busy
  photograph without a scrim.
- Never redraw or substitute a mark. If a size demands better fidelity than a
  PNG gives, render from the vector PDF rather than upscaling.

---

## Tables

Tables carry most of PLX's actual content — formulas, BOMs, COAs, digests — so
they matter more here than in most brands. There is deliberately **no
brand-specific table component**: the token layer covers both AG-Grid (heavy
grids) and shadcn `<Table>` (light ones).

| Aspect | Rule |
|---|---|
| Header row | Mono, uppercase, tracked `0.16em`, `--p-muted`, on `--p-paper-2` |
| Body text | Sans, `--p-ink-2` |
| Numeric cells | **Mono with tabular numerals** — always. Percentages and quantities must line up vertically |
| Alignment | Text left · numbers right · dates and IDs left in mono |
| Row separators | 1px hairline `#D7D6D2`. Nothing heavier |
| Zebra striping | **No.** Hierarchy comes from hairlines, not fills |
| Row hover / active | `--p-paper-2` recess |
| Borders | Hairlines only. No drop shadows, no heavy outer frame |
| Totals row | Hairline above, mono, `--p-ink`, optionally `--p-paper-2` |
| Status in cells | The status **text** shade, or a chip on the soft tint — never a saturated fill |
| Empty optional rows | Remove the row entirely. Never render "—" or `undefined` in long-form sections |

That last rule is a documented PLX convention, not a stylistic preference:
empty fields drop their whole row.

**In Excel specifically:** freeze the header row, set numeric columns to a mono
face with a consistent decimal count, right-align them, and use a 0.5pt hairline
in `#D7D6D2` for gridlines rather than Excel's default grey. Kill the
default blue-white "Table Style" — it is aggressively off-brand.

---

## Documents, letterheads and agreements

The token scale is defined for screen. For print, Word and PDF use this mapping;
it preserves the hierarchy ratios at document scale. This print mapping is a
documented adaptation — `tokens.css` specifies screen px only.

| Element | Face | Size | Colour |
|---|---|---|---|
| Document title | Mazius Display (or Georgia) | 26–30 pt | `#1B1A17` |
| Section heading | Inter Semibold (or Segoe UI Semibold) | 12–13 pt | `#1B1A17` |
| Body | Inter Regular | 10.5–11 pt / 1.5 line | `#3A3833` |
| Running head / ref line | Mono, uppercase, `0.16em` | 7.5–8 pt | `#6B665B` |
| Table header | Mono, uppercase, `0.16em` | 8 pt | `#6B665B` |
| Footer boilerplate | Inter Regular | 8 pt | `#6B665B` |
| Rules and hairlines | — | 0.5–0.75 pt | `#D7D6D2` |

**Structure a PLX document like a folio:**

1. **Logo** — horizontal ink lock-up, top left, around 35 mm wide.
   Beyond that, place the vector PDF rather than the PNG.
2. **Running head** — mono uppercase: `PLX · 02 · SUPPLY AGREEMENT` upper left,
   the reference (`2614/2026 · [Matter]`) upper right.
3. **Title** in the serif face, at most one italic accent word.
4. **Hairline rule** — never a filled banner, never a drop shadow.
5. **Body** in the sans face, generous leading.
6. **Footer** — `[Entity]` · `[Contact]` · confidentiality note, muted 8 pt.
   Do not invent a legal name, address, or phone.

**Fonts on someone else's machine:** Mazius Display and Inter must be installed
for a `.docx` to render as intended. If you cannot confirm they are, either
embed the fonts in the file or fall back to Georgia and Segoe UI — and say
plainly that you substituted. Never ship a file that silently renders in Calibri.

Page ground is paper `#FBFAF6`, not white.

---

## Email

Email clients cannot resolve CSS variables, so the palette is mirrored as
literal hex from the same tokens. Inside the portal, **always** build through
`portal/src/lib/notifications/email-theme.ts` and `emailShell` — never hand-roll
inline HTML in a route, script, or agent session. Structure lives in
`docs/design-system/EMAIL-STYLE-SOP.md`.

| Role | Token | Hex |
|---|---|---|
| Page background / footer band / KV inset | `--p-paper-2` | `#ECEFE9` |
| Card | `--p-paper` | `#FBFAF6` |
| Header bar / buttons | `--p-ink` | `#1B1A17` |
| Text on ink | `--p-paper` | `#FBFAF6` |
| Headings | `--p-ink` | `#1B1A17` |
| Body copy | `--p-ink-2` | `#3A3833` |
| Kicker / meta / footer | `--p-muted` | `#6B665B` |
| Hairline / soft hairline | `--p-grid` / `--p-grid-2` | `#D7D6D2` / `#E9E8E4` |

Kicker mono 11/0.16em caps muted · title Georgia 22/1.3 ink,
sentence case, ≤1 italic accent `<em>` · body sans 14/1.65 · footer mono
10/0.14em caps · button mono 12/0.08em caps, **one per email**.

Working-surface buttons and status pills are **radius 0** (sharp rectangles).
Cards use `4px`. The shipped email module still uses
`4px` on buttons (EMAIL-STYLE-SOP v1.1) — that is leftover
email geometry, not the working-surface rule. Do not invent a third radius.
Do not hand-roll a different email button.

Shells and buttons are **table-based with `bgcolor`**, not divs. Sentence case
everywhere; uppercase only via tracked mono. No shadows, gradients, images,
icons or emoji.

### Email signature

The signature template is **deliberately not filled** — it would carry personal
contact information. Structure only. Get the actual values from the person:

```
[Name]
[Title] · Petra Lab-X
[email] · [phone]
──────────────────────────  ← hairline #D7D6D2
PLX · PETRA LAB-X            ← mono, uppercase, 0.16em, #6B665B
```

Name in sans semibold `#1B1A17`; title and contact in sans
`#3A3833`; the tracked mono lockup line in `#6B665B`.
Logo optional — if used, the horizontal ink lock-up, small (email renders
at screen resolution, so the PNG is fine).
**Do not invent contact details, a legal entity name, an address, or a phone.**

---

## Per-format quick reference

**Word (.docx)** — Set Styles rather than direct formatting so the document
stays editable: Title → serif 28pt ink; Heading 1 → sans semibold 13pt ink;
Normal → sans 10.5pt `#3A3833` at 1.5; a "Meta" character style →
mono 8pt caps tracked `#6B665B`. Header/footer carry the running head
and boilerplate. Embed fonts if the recipient may not have them. Page
`#FBFAF6`.

**Excel (.xlsx)** — Header row mono caps tracked on `#ECEFE9`,
frozen. Numerics mono, right-aligned, tabular, consistent decimals. Hairline
gridlines `#D7D6D2`. No zebra fills, no default Table Styles, no
saturated conditional-formatting scales — use the derived status soft tints
if you must colour cells.

**PowerPoint (.pptx)** — Paper `#FBFAF6` ground, not white. Title
slide: serif title with one italic accent word, mono tracked kicker above it,
horizontal ink logo bottom-left — use the vector PDF if you scale it past
~35 mm, since deck logos are often placed large. Body slides: sans,
hairline rules for structure, no shadows or gradients. Accent is rationed —
one per slide at most.

**PDF** — Follow the Word mapping. Ensure hairlines are ≥ 0.5pt so they survive
flattening.

---

## Chassis-and-folio vocabulary

PLX traffics in formulas, certificates and signed authorisations — all of which
have print heritage. The chrome quotes that heritage:

- **Folio borders** — hairline rules at page edges with mono running heads.
- **Chassis ticks** — small `+` marks at the four corners of cards and primary
  blocks. Structural, not ornamental.
- **Hairlines for hierarchy** — 1px translucent ink. No drop shadows. No filled
  rounded containers as a default. Cards exist but are barely there.
- **Radius** — cards `4px`, pills/tints `3px`,
  quote tiles `6px`. **Buttons and status pills have no
  radius at all — sharp rectangles.** Do not apply the card token to a CTA.
- **Hover** — cards wake by darkening the border (`--p-grid` → `--p-ink-2`),
  never lifting. Buttons: ink fill → forest on hover. Ghost: border hairline
  → ink. Links: forest underline at 2px offset. No scale, glow, shrink, or
  bounce.

## Voice and copy

- Voice: plain, confident, operational. "A *partner*, not a vendor."
- Person: customer as **you**; PLX as **PLX** or **we**.
- Casing: sentence case UI; UPPERCASE only tracked mono
  (`0.16em` / `0.22em`).
- Tone: matter-of-fact status; calm attention prompts.
- Headlines: serif with exactly one italic forest accent word.
- Domain vocab: product briefs, tech transfers, formulations, BOM,
  manufacturing orders, onboarding, approvals, credit application,
  FM codes / FM Ref, SharePoint, DocuSign; product nouns hand balm,
  hand cream, stick.
- Numbers: mono tabular. Emoji never.

## Iconography

Lucide line icons only, 1.5–2px stroke, `16px` rows / 20px stat
cards, muted default, ink when active. Never invent SVG icons or use emoji
as icons. `--p-icon-lg` is `32px` for header/hero.

## Layout (app surfaces)

Fixed 64px header, 256px sidebar. Content on `--p-canvas`
(`#F5F3EC`), cards on `--p-paper` (`#FBFAF6`).

## Provenance and precedence

| Source | Role |
|---|---|
| `design-system/tokens.css` v1.3.0 | Authority for every value (ADR-005) |
| Claude Design project + SharePoint exports | Provenance for voice, iconography, interaction |

Claude Design palette is **STALE** (`#FBF9F5` / `#F2EDE2` / `#807A6F`).
Current: `#FBFAF6` / `#ECEFE9` / `#6B665B`.
Take values from `tokens.css`; take voice / iconography / interaction from
the Claude Design doc.

Spacing (`--p-space-*`):
`4 · 8 · 14 · 22 · 32 · 48 · 72`.

Motion (`--p-dur-*` / `--p-ease`): `120ms` fast, `180ms`
default, `320ms` slow, on `cubic-bezier(0.2, 0.8, 0.2, 1)`.

**Why muted, always:** PLX users see the same project for weeks. A dashboard
that shouts a green tick and a red cross every render trains people to ignore
those signals. Muted earth tones force the user to read the label — which is
what we want them reading anyway.

---

## What "wrong" looks like

- Saturated Tailwind/Bootstrap status colours.
- Reading ADR-001 for accent or body face (stale rust / Geist).
- Mazius Display set as body copy, or mono running as body text.
- More than one italic accent word in a headline.
- Zebra-striped tables, default Excel Table Styles, heavy grid borders.
- Drop shadows, glassmorphism, aurora gradients. (Those belong to the public
  homepage — a deliberately different surface, out of scope here.)
- Rounded or pill buttons / status chips (card radius `4px`
  applied to a CTA).
- Upscaling a logo PNG when the vector PDF would render it cleanly.
- A logo recoloured, stretched, or substituted.
- Inventing a second voice, a legal entity line, a phone number, or a
  signature contact.
- Raw hex in portal code instead of a `--p-*` token.
- Pure white `#FFFFFF` grounds. The brand's ground is paper `#FBFAF6`.

---

## What this skill cannot give you

Flag these and ask rather than inventing:

- **Legal entity name** and registered address — not in the repo.
- **Phone numbers and postal addresses** for footers.
- **Personal contact details** for email signatures — structure only, by design.
- **Confidentiality / legal boilerplate** — must come from PLX counsel, not from
  a design artifact.

---

## In-repo surfaces

If you are working inside this repository:

- Spec / authority — `design-system/tokens.css`
- Runtime mirror the app imports — `portal/src/styles/brand-tokens.css`
  (Turbopack cannot import CSS from outside the app root, hence two files —
  **keep them in sync**; drift is a hygiene failure)
- Typed export — `design-system/tokens.ts` (generated; never edit values there)
- Narrative, inventory, ADRs — `docs/design-system/`
- Brand assets — `docs/design-system/assets/`
- Runtime lock-ups + SVG favicons — `portal/public/brand/`
- Email — `docs/design-system/EMAIL-STYLE-SOP.md` and
  `portal/src/lib/notifications/email-theme.ts`
- Versioned kit — `artifacts/design-system/brand-kit-v1.3.0/`

Brand styling activates via `data-brand="plx"` on `:root` or a `.brand-plx`
class. Surfaces that should stay unbranded omit it.

After changing any artifact in `design-system/`, run
`python3 scripts/design-system-manifest.py`, bump `version` in `manifest.json`,
add a `CHANGELOG.md` entry, then
`python3 scripts/generate-plx-brand-skill.py` and
`python3 scripts/generate-plx-brand-kit.py`.
`design-system-release.yml` fails the PR if the skill or kit is stale.
