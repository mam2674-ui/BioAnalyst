# BioAnalyst — Design System

<!-- impeccable:design-schema 1 -->

Mode: **Operate** (the visitor completes a research task; scanability and
consistency outrank expression — see PRODUCT.md). Color strategy:
**Restrained** (neutrals plus one accent; color does real jobs — active
filters, the primary action color, the one hero moment — never a full-bleed
wash across a data page).

## Direction contract

**THESIS.** One accent color and one soft atmospheric gradient, spent once at
the top of the homepage, carries the whole platform's identity — every other
page stays a clean, high-density research surface in the same restrained
palette. The category default this refuses: either no visual identity at all
(bare Streamlit defaults, which is where this app started), or a template
redecoration repeated identically on all 8 pages (a gradient banner stamped
on every header, which reads as decoration-by-template rather than a
deliberate single moment).

**OWN-WORLD.** A pale blue-to-white atmospheric gradient (inspired by, and a
deliberate restraint-translation of, untillabs.com's sky-gradient hero) is
reserved for exactly one surface: the Home page's hero panel. Everywhere else,
the surface is white/near-white with a single accent blue. Pill-shaped
controls (buttons, selects, multiselect filter tags) are the one shape
language carried everywhere, translating untillabs' pill nav/CTA language
into functional filter chips rather than marketing buttons. Bold, tightly
tracked headings (system sans-serif, no custom display face — Operate mode is
explicitly well served by a system stack) are the type signature.

**STORY.** A first-time visitor lands on Home, sees one clear visual moment
(the gradient hero panel) that states the product name, which sector is
active, and the one question that sector answers — then moves into 7 pages
that look like the same product but never fight the data for attention.

**FIRST VIEWPORT.** Home.py's hero: `st.container(key="hero")` rendered with
a `.st-key-hero` CSS gradient background (see Tokens), containing the bold
"BioAnalyst" title, a caption subtitle, and a two-column asymmetric pairing —
the active sector name large on the left (3 parts width), the sector's central
question smaller on the right (2 parts width) — directly adapting untillabs'
"bold statement left / supporting detail right" pairing.

**FORM.** Built code-led, in-thread, without the full concept-seed/decision-page
pipeline (no image-generation tool or decision-page server available in this
session; the visual direction was instead pinned directly by the user's own
choice between two concrete options, which stands in for that round). No
named subagents (`impeccable-asset-producer` / `impeccable-finish-reviewer`)
were available either — this build and its own verification were both done
in-thread, disclosed here rather than silently.
`seed: none (unavailable)`

**FINISH.** Unreviewed and undocumented is unfinished; this build ends with
the finish review, the verdict, DESIGN.md, and every shipping raster carrying
its provenance. (No rasters were produced in this build — the hero is pure
CSS/gradient, no generated imagery — so there is nothing to provenance-tag.)
Finish review here was an in-thread browser-pane inspection (desktop 1440px,
mobile 375px, 3 of 8 pages spot-checked, console-clean), not the shipped
`impeccable-finish-reviewer` subagent, disclosed per the substitution rule
above.

## Tokens

### Color

| Role | Value | Where |
|---|---|---|
| `accent` | `#2451B8` | `.streamlit/config.toml` `primaryColor` — buttons, active filter pills, focus states, selected nav item |
| `background` | `#FFFFFF` | page background |
| `surface-tint` | `#EEF2FC` | `secondaryBackgroundColor` — sidebar, `st.info`/`st.warning` boxes, bordered containers |
| `text` | `#15181F` | body/heading text |
| `hero-gradient` | `linear-gradient(135deg, #EEF2FC 0%, #DCE6FA 55%, #FFFFFF 100%)` | `.st-key-hero` only — the one spent hero moment |

Contrast checked: white text on `#2451B8` ≈ 7.1:1 (exceeds WCAG AA, approaches
AAA). `#15181F` text on `#FFFFFF` or `#EEF2FC` is effectively maximum contrast.

### Shape

- `rounded.control` = `999px` (pill) — every `st.button`, `st.selectbox`,
  `st.multiselect` tag, applied via `.stButton > button`,
  `div[data-baseweb="select"] > div`, `div[data-baseweb="base-input"]`.
- `rounded.panel` = `24px` — the hero container only.

### Type

System sans-serif stack (Streamlit `font = "sans serif"`), no custom display
face — Operate mode is explicitly well served by system/workhorse stacks
(no subject association forces a custom face here). Headings (`h1`) at 700
weight, `-0.02em` tracking; `h2`/`h3` at `-0.01em`. Metric values bolded.
Body text untouched (Streamlit defaults, already AA-safe).

### Components

- **Hero panel** (`.st-key-hero`, Home.py only): gradient background,
  24px corner radius, bold title + caption + asymmetric two-column pairing.
  Never repeated on another page — see THESIS.
  Implementation: [bioanalyst/ui_common.py](bioanalyst/ui_common.py)
  (`inject_design_system`), [Home.py](Home.py).
- **Context panel**: `st.container(border=True)` for the active-sector
  callout — unchanged from the prior layout pass, now inherits pill/color
  tokens.
- **Stat row**: `st.container(border=True)` wrapping `st.columns(4)` of
  `st.metric` — unchanged structurally, now bold metric values.
- **Filter pills**: `st.multiselect` tags (Market Overview's sidebar filters)
  — unaffected structurally, now accent-colored and pill-shaped for free via
  the shared CSS + theme.

## What this redesign deliberately did not touch

- The emoji-as-icon system (sector icons 🧬/🧠, claim-type badges
  🟢/🟡/🔷/🔵, ⚠️/🔄 in captions) — flagged in the prior audit as a
  craft-floor default to avoid, but replacing it is a content/icon-library
  decision across every page's data display, not a color/shape/type system
  change. Left as a named follow-up.
- The sidebar not auto-collapsing on narrow/mobile viewports — a Streamlit
  framework default, pre-existing, not part of this visual pass.
- Plotly chart color palettes (Market Overview's bar charts) — still
  plotly-express defaults; not re-themed to the accent color in this pass.
- The 7 inner pages' internal data layout (tables, forms, columns) — Operate
  mode's own discipline says brand lives in precise details, not loud
  per-page redecoration; they inherit the shared system (color, pills, type)
  without being individually rebuilt.
