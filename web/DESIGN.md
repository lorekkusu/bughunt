# bughunt Report Site — Design Brief

*Svelte 5 + Tailwind v4 · dark + light · premium-but-honest dev-tool · our own voice, inspired by (not cloned from) State of JS. Palette below is validated with the dataviz CVD script — results inline.*

---

## 1. Identity — two directions, one recommendation

### ▸ Direction A — "Casefile" *(RECOMMENDED)*
A reproducible **lab notebook / evidence log** for a bug hunt. The page reads like a careful investigator writing up findings: prose in a cold geometric sans, but the **data speaks in monospace** — every figure, tool ID, tag, axis tick, and `✅ ⚠️ ❌` stability glyph is mono with tabular figures. That split (sans narration / mono evidence) is our signature and is exactly what separates us from State of JS, which monospaces *everything*.

- **Mood:** quiet, forensic, confident. Warm near-black and warm paper (not `#000/#fff`), hairline **dotted** rules as case-file dividers, rank gutters, N-counts shown next to every percentage.
- **What makes it feel crafted:** `✅/⚠️/❌` treated as a first-class typographic system, not emoji decoration; tabular figures that align to the pixel; every chart carries a one-line human sentence + a definition banner; six designed microstates on every interactive mark.
- **How it signals honest/informal-but-careful:** an inline **caveats box** ("single LLM judge, one language, list-price estimates"), the absolute **N** beside every proportion, the **zero false-positives** shown as an exact held `0.0`, and a chart↔table toggle everywhere. Informal in voice ("So what do I use?"), rigorous in evidence.

### ▸ Direction B — "Blueprint" *(alternative)*
Vercel/Linear-style architectural minimalism: hairline grid, high-contrast cold monochrome, one accent, no warmth, mono reserved strictly for code. Cleaner and more corporate — but it under-sells the bug-hunt/evidence story and the informal honesty we want. Reads "infra dashboard," not "field report."

**Recommendation: A (Casefile).** It leans into the code-review/evidence theme, carries the honesty signals natively, and gives us a distinct point of view versus the obvious reference.

---

## 2. Design system

### Categorical — fixed tool order (never cycled, never repainted by rank)
Order groups *general coding models* then *native specialist reviewers*; each tool owns its hue in every leaderboard, scatter, and curve. **Validated** (light worst-adjacent ΔE 9.7 floor-band → relief via legend + direct labels, which we always ship; dark worst-adjacent ΔE 13.8, clear).

| # | Tool | Hue | Light | Dark |
|---|------|-----|-------|------|
| 1 | **composer** (cursor) | blue | `#1f77c4` | `#4a97e6` |
| 2 | **opus** (claude) | orchid | `#b95fb0` | `#c56cbb` |
| 3 | **codex** (gpt) | vermillion | `#d94f1a` | `#e86a3a` |
| 4 | **bugbot** (cursor, native) | teal | `#0a9d78` | `#17a37c` |
| 5 | **coderabbit** (native) | amber | `#e0a01e` | `#b8871c` |

Max 5 series here; if the entity set ever grows past ~8, fold to "Other"/small-multiples. Effort tiers *within one model* (low→max) are **not** categorical — they use the sequential ramp below.

### Sequential — recall / magnitude (one hue, blue, light→dark)
- **Recall heatmap (3-step ordinal):** never `❌` / some `⚠️` / every `✅` — always paired with the glyph so it's never color-alone.
  - Light: never `#e8eef7` · some `#6da7ec` · every `#1c5cab`
  - Dark: never `#1e2633` · some `#3f6fb0` · every `#7fb0ee`
- **Continuous recall / effort ramp:** blue `#cde2fb → #0d366b` (light), inverted toward surface on dark. Second simultaneous sequential context borrows teal.

### Diverging — deltas (two poles + neutral gray midpoint)
**blue ↔ vermillion**, gray midpoint (light `#f0efec`, dark `#383835`). Used for signed change only (e.g., recall Δ vs. effort baseline, over/under a reference). Never a hue at the midpoint. Diverging and categorical never co-occur in one chart, so the shared red is unambiguous.

### Status — RESERVED (FP severity + bug severity), always icon+label, never "series 6"
| role | hex | use |
|---|---|---|
| good | `#0ca30c` | 0 FP; low-severity bug |
| warning | `#fab219` | medium severity |
| serious | `#ec835a` | high severity |
| critical | `#d03b3b` | noisy FP; critical bug; the S4 "wall of red" |

Fixed across themes (all ≥3:1 on the dark surface; warning/serious sub-3:1 on light are mitigated by mandatory icon+label).

### Surfaces (validator inputs)
- **Light** surface `#fbfaf8` · page plane `#f7f6f3` · ink `#16150f` / secondary `#57544c` / muted `#8a877e` · hairline `#e4e1d8`
- **Dark** surface `#17161a` · page plane `#0c0b0a` · ink `#f4f2ea` / secondary `#b6b2a6` / muted `#85817a` · hairline `#2a2823`
- Dark mode is **designed from the ramps against `#17161a`**, not auto-flipped (see dark columns above).

### Type system
- **Display + body:** Geist (fallback Inter) — cold, geometric. Big jump hero→body carries hierarchy.
- **Mono (the "evidence voice"):** Geist Mono (fallback JetBrains Mono) — all figures, tool IDs, tags, axis ticks, `✅/⚠️/❌`, code. `font-variant-numeric: tabular-nums` on every aligned column.
- **Scale (~1.2 modular):** 12 / 13 / **14 base** / 16 / 20 / 28 / 44 / 72 (hero). Text always in ink tokens, never series color.

### Spacing rhythm
4px base, 8-pt grid: **4 / 8 / 12 / 16 / 24 / 32 / 48 / 64 / 96**. Section gaps 96–128 ("enough, then double it"). Hairline (0.5–1px, low-alpha) and dotted case-file dividers instead of card shadows.

### Motion principles
Animate: first-scroll reveals (once), KPI count-ups, bar grow-from-baseline, line/scatter draw-in, the two signature cascades. **Stays still:** no loops, no parallax, no scroll-jacking, no motion on hover except affordance highlight + tooltip; ranks never idly reshuffle. All gated on `prefersReducedMotion` (→ duration 0). One easing (`cubicOut`), durations ≤250ms except the two signatures (~600ms staggered).

---

## 3. Information architecture (hero → conclusion)

| # | Section | Data | Form | Palette role |
|---|---------|------|------|--------------|
| 1 | **Hero** | composer 100/94/92%, 0.0 FP, ~$0.17/run | Hero number + 3 stat tiles (no chart) | ink + one good-green `0.0` |
| 2 | **How to read this** (method strip) | recall def, `✅⚠️❌` key, judge/cost caveats, 3 runs | Inline caveat box + definition legend | status + sequential key |
| 3 | **The leaderboards** | 12 configs × 3 projects (recall/FP/$) | Small-multiple ranked horizontal bars (3 panels), sorted by recall, **fixed tool hue**, medal icons | categorical |
| 4 | **The recall matrix** ★ | bug × config, found-count 0–3 | **Heatmap**, 3-step ordinal + in-cell glyph, small-multiple per project | sequential (blue) |
| 5 | **Effort is a tax** | recall vs effort, codex & opus per project | Slope/line, ordinal x, endpoint direct-labels, small-multiple | categorical (2 lines) |
| 6 | **The value frontier** | recall vs est. $/run per config | Scatter + Pareto line; annotate composer, opus-`max`; native tools flagged | categorical |
| 7 | **The precision axis** | FP/run; recall as 2nd measure | Recall-vs-FP scatter (**not** dual-axis) or ranked FP dot plot; zeros highlighted | status (reserved) |
| 8 | **The bug that beat everybody** ★ | pricing C1: 32/33 miss | Unit chart, 33 cells, one lit; big "1 / 33" stat | status critical + good |
| 9 | **The specialists lost** | CodeRabbit/Bugbot vs field + bonus | Ranked bar / bump chart, two specialists tagged | categorical |
| 10 | **So what do I use?** | synthesized verdicts | 3–4 recommendation cards, each with a stat tile | categorical accents |
| 11 | **Method & full tables** (appendix) | every config, all metrics | Sortable data table = mandated a11y fallback | ink |

★ = the two (only two) signature animated moments.

---

## 4. Component inventory

- **ToolChip** — fixed-hue swatch + mono label; the identity token reused everywhere.
- **LeaderboardRow** — rank/medal gutter, ToolChip, grow-in bar, recall %, FP, $/run, N; six microstates.
- **StatTile / KPI** — big tabular number + label + optional delta; count-up.
- **HeroNumber** — oversized recall figure + one-line dek.
- **HeatmapCell** — 3-step ordinal fill + `✅/⚠️/❌` glyph + found-count tooltip; 2px surface gap between cells.
- **HeatmapGrid** — rows grouped by severity (crit→low), cols = configs, small-multiple per project.
- **EffortCurve** — ordinal-x slope/line, endpoint-only direct labels.
- **ValueFrontierScatter** — fixed-hue points, traced Pareto frontier, annotated outliers, native-tools callout.
- **PrecisionPlot** — recall-vs-FP scatter or FP dot plot; reserved-status highlight on the zeros.
- **UnitChart** — 33-cell wall for S4.
- **DefinitionBanner** — metric definition above each chart.
- **CaveatBox / MethodStrip** — the honesty inline.
- **SectionHeader** — mono kicker + display title + dek.
- **RecommendationCard** — verdict + supporting StatTile.
- **DataTable** — sortable, tabular figures; the chart↔table fallback for every viz.
- **Legend** (fixed-order, ≥2 series only), **ThemeToggle**, **TableToggle**, **SourceRow/Footnote** (N, export/share).

---

## 5. Tech plan

**Structure — single prerendered page**, sections as `lib/components`. **Charts — hand-rolled SVG + `d3-scale`** (`d3-shape` only for line/area paths); LayerChart is the fallback if the scatter's quadtree hit-testing gets fiddly. SVG marks read `fill="var(--tool-composer)"` etc., so theme flips with zero re-render. Static via `@sveltejs/adapter-static`, `prerender = true`, `ssr = true`.

```
src/
  app.css                 # Tailwind v4 entry, @custom-variant dark, :root + .dark CSS vars (palette above)
  app.html                # pre-paint inline theme script (no flash)
  routes/
    +layout.ts            # prerender = true; ssr = true
    +page.ts              # load(): import typed dataset (build-time inlined)
    +page.svelte          # composes sections, owns scroll container
  lib/
    types.ts              # Benchmark, Config, Project, BugCell, Tool
    data/
      benchmark.json      # parsed from RESULTS.md / harness/reports
      benchmark.ts        # `raw satisfies Benchmark`; precompute leaderboards, extents, frontier at module scope
    theme.svelte.ts       # $state light/dark, localStorage, sets .dark on <html>
    actions/reveal.ts     # IntersectionObserver reveal (once, ~15%)
    charts/               # Chart.svelte frame, Bars, Heatmap, Slope, Scatter, UnitChart, scales.ts, a11y.ts
    components/           # Hero, StatTile, LeaderboardRow, ToolChip, EffortCurve, ValueFrontier,
                          # PrecisionPlot, RecommendationCard, CaveatBox, DefinitionBanner, DataTable, ThemeToggle
```

**Data → typed site data:** the RESULTS/summary tables are transcribed once into `benchmark.json`, type-checked via a hand-written `Benchmark` type, and all derived views (per-project leaderboards, recall matrix, Pareto frontier, extents) computed **once at module scope** (data is fixed) — `$derived` reserved only for UI-toggle-driven views (active project tab, chart↔table). Palette lives as CSS custom properties consumed by `fill`/`stroke`.

**Three signature animated moments (with restraint):**
1. **Heatmap cascade (§4).** On first scroll-in, cells fill column-by-column (~600ms staggered, once) — the near-solid dark grid resolves and the 2–3 glaringly empty columns (`M2 float-money`, `L2 broad-except`, `L3 crash`) *stay* light. The payoff is the negative space.
2. **Wall of red (§8).** 33 cells flash `critical` in a quick stagger; one composer cell flips to `good` and a `1 / 33` figure counts up. Then everything holds still.
3. **Honest hero count-up.** Hero recall and the three tiles count from 0 (`Tween`, `cubicOut`); the FP tile lands on and holds exactly `0.0` in good-green. Leaderboard bars grow from baseline once. Nothing else animates.

---

## 6. Cheap-vs-premium guardrails (project-specific)

- **N + `✅⚠️❌` are non-negotiable** — every % ships its absolute run-count and stability glyph. Absence reads as a marketing chart, not a benchmark.
- **Never repaint a tool by rank.** composer is blue in the podium, the scatter, and last-place alike. A tool changing color across charts is the #1 tell here.
- **No dual-axis, ever** — recall and FP (§7) get a scatter or two small-multiples, never two y-scales.
- **Status colors stay reserved** — the amber/red of FP severity must never leak in as a 6th tool hue; conversely no tool hue in a severity slot.
- **The heatmap earns the vertical space; nothing else copies its motion.** Exactly two signature reveals — a third cheapens all three.
- **Table view + `prefersReducedMotion` are shipped, not stubbed** — every chart has a real sortable fallback; reduced-motion means truly static.
- **Warm near-black/paper, not `#000/#fff`; dotted case-file rules, not card shadows** — the moment it grows equal-tile KPI cards, drop-shadows, or a rainbow legend, it's an admin panel.
- **One held `0.0`, honestly.** The zero-FP claim is the credibility centerpiece — show it as an exact figure with the good-green status + label, never rounded away or dramatized.

*Palette validation: categorical set passes the dataviz CVD script in both modes (light min-adjacent ΔE 9.7 with mandatory legend+labels relief; dark 13.8 clear; all in lightness band, chroma floor, contrast).*
