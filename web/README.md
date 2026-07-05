# bughunt — report site

The static report site for the [bughunt](../) benchmark. Everything you see is
**derived from the harness at build time** — there is no hand-maintained data in
here, so the page can never drift from the results.

- **Data:** `../harness/config.toml` (tool identity + colours), `../harness/results/**`
  (the numbers), and `../RESULTS.md` (the vetted interpretation).
- **Stack:** SvelteKit 5 + Tailwind v4, prerendered to static HTML
  (`@sveltejs/adapter-static`). Charts are hand-rolled SVG (no chart-lib dependency).
- Design brief: [`DESIGN.md`](./DESIGN.md).

## Develop

```sh
pnpm install
pnpm dev          # regenerates data (predev) then starts Vite
```

Open http://localhost:5173.

## Build

```sh
pnpm build        # pnpm gen (data + results + copy) → vite build → build/
pnpm preview      # serve the production build locally
```

`BASE_PATH` sets a subpath for a GitHub Pages project site (e.g. `/bughunt`);
leave it empty for a root/custom-domain deploy. Asset paths are relative, so the
output is portable across hosts.

## How the data is generated

Three scripts run before Vite (wired into `pnpm gen`, `predev`, and `build`).
Their outputs live in `src/lib/{data,generated}/` and are **gitignored** —
regenerated every build, never committed, so they can't go stale:

| script | reads | writes |
|--------|-------|--------|
| `scripts/build-data.mjs` | `harness/config.toml` + `harness/results/**` | `src/lib/data/benchmark.json`, `src/lib/generated/palette.css` |
| `scripts/build-results.mjs` | `RESULTS.md` | `src/lib/data/results.json` (prose + inline-chart blocks) |
| `scripts/build-copy.mjs` | the above two | `src/lib/generated/copy.md` (the "copy for AI" snapshot) |

To change what the site shows, edit the **source** (`config.toml` / results /
`RESULTS.md`) and rebuild — never edit the generated files or hardcode data in a
component. Add a provider (with a `color`) or a project in `config.toml` and the
site picks it up automatically.

## Deploy

`.github/workflows/deploy-web.yml` builds and deploys to GitHub Pages on every
push to `main` that touches the site or the data. It needs Pages enabled
(Settings → Pages → Source: GitHub Actions); GitHub Pages on a private repo
requires a paid plan, otherwise make the repo public or deploy the `build/`
output to Cloudflare Pages / Netlify / Vercel instead.
