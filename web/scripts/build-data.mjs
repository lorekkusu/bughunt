// Derive the ENTIRE site dataset from the harness — no hardcoded tool/project
// knowledge. Identity, labels and colours come from harness/config.toml; the
// numbers come from harness/results/**.json. A subject is a (provider, MODEL)
// pair — a provider can run several models — shown as model-name primary +
// provider secondary. Adding a provider/model/project or changing a colour in
// config.toml is picked up automatically on the next build.
// Emits src/lib/data/benchmark.json + src/lib/generated/palette.css.
import { readdirSync, readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parse as parseToml } from 'smol-toml';

const here = dirname(fileURLToPath(import.meta.url));
const HARNESS = join(here, '..', '..', 'harness');
const RESULTS = join(HARNESS, 'results');
const OUT = join(here, '..', 'src', 'lib', 'data', 'benchmark.json');
const CSS = join(here, '..', 'src', 'lib', 'generated', 'palette.css');

const round = (x, n = 4) => (x == null ? null : Math.round(x * 10 ** n) / 10 ** n);
const SEVERITIES = ['critical', 'high', 'medium', 'low'];
const slug = (s) =>
	String(s)
		.toLowerCase()
		.replace(/[^a-z0-9]+/g, '-')
		.replace(/^-|-$/g, '');
const mean = (xs) => {
	const v = xs.filter((x) => x != null);
	return v.length ? v.reduce((s, x) => s + x, 0) / v.length : null;
};

// ---- config.toml: the source of truth for identity + colour ------------------
const cfg = parseToml(readFileSync(join(HARNESS, 'config.toml'), 'utf-8'));

// providerMeta[key] holds provider-level display + a per-model lookup.
const providerMeta = {};
const providerOrder = [];
for (const [key, p] of Object.entries(cfg.providers ?? {})) {
	providerOrder.push(key);
	const models = p.models ?? [];
	const modelLabels = p.model_labels ?? [];
	const modelColors = p.model_colors ?? [];
	const modelColorsDark = p.model_colors_dark ?? [];
	providerMeta[key] = {
		key,
		label: p.label ?? key, // provider display name (secondary)
		kind: p.manual ? 'manual' : p.native ? 'native' : 'model',
		byModel: Object.fromEntries(
			models.map((m, i) => [
				m,
				{
					modelLabel: modelLabels[i] ?? m,
					color: modelColors[i] ?? p.color ?? '#888888',
					colorDark: modelColorsDark[i] ?? p.color_dark ?? p.color ?? '#999999'
				}
			])
		),
		fallback: { color: p.color ?? '#888888', colorDark: p.color_dark ?? p.color ?? '#999999' }
	};
}
const projectOrder = (cfg.projects ?? []).map((p) => p.name);
const projectTheme = Object.fromEntries((cfg.projects ?? []).map((p) => [p.name, p.theme ?? '']));
const projectMode = Object.fromEntries(
	(cfg.projects ?? []).map((p) => [p.name, p.review_mode === 'diff' ? 'diff' : 'tree'])
);

// canonical effort order = union of providers' `efforts` in declaration order.
const effortOrder = [];
for (const key of providerOrder)
	for (const e of cfg.providers[key].efforts ?? [])
		if (!effortOrder.includes(e)) effortOrder.push(e);

const toolIdOf = (provider, model) => slug(model); // model-unique; asserted below

// ---- results/**.json: the numbers -------------------------------------------
function walk(dir) {
	const out = [];
	for (const e of readdirSync(dir, { withFileTypes: true })) {
		const p = join(dir, e.name);
		if (e.isDirectory()) out.push(...walk(p));
		else if (e.name.endsWith('.json')) out.push(p);
	}
	return out;
}

const configs = [];
const bugsByProject = {};
const baseBugsByProject = {};
const seenPairs = new Set(); // `${provider}/${model}`

for (const f of walk(RESULTS)) {
	const d = JSON.parse(readFileSync(f, 'utf-8'));
	const pm = providerMeta[d.provider];
	if (!pm) {
		console.warn(`skip result for unregistered provider "${d.provider}" (${f})`);
		continue;
	}
	seenPairs.add(`${d.provider}/${d.model}`);
	if (!bugsByProject[d.project]) {
		bugsByProject[d.project] = d.planted.map((b) => ({
			id: b.id,
			severity: b.severity,
			title: b.title,
			file: b.file,
			symbol: b.symbol,
			...(b.distance ? { distance: b.distance } : {})
		}));
	}
	// diff-mode: pre-existing base bugs are a separate axis (never recall/FP)
	if (d.base_bugs?.length && !baseBugsByProject[d.project]) {
		baseBugsByProject[d.project] = d.base_bugs.map((b) => ({
			id: b.id,
			severity: b.severity,
			location: b.location,
			title: b.title,
			file: b.file
		}));
	}
	const m = d.metrics;
	configs.push({
		tool: toolIdOf(d.provider, d.model),
		provider: d.provider,
		model: d.model,
		effort: d.effort,
		project: d.project,
		promptId: d.prompt_id,
		native: pm.kind === 'native',
		manual: pm.kind === 'manual',
		runs: d.runs,
		recall: { mean: round(m.recall.mean), min: round(m.recall.min), max: round(m.recall.max) },
		fp: round(m.false_positives.mean, 2),
		bonus: round(m.bonus.mean, 2),
		speedS: m.elapsed_s.mean == null ? null : Math.round(m.elapsed_s.mean),
		cost: m.cost_usd?.mean == null ? null : round(m.cost_usd.mean, 4),
		perBug: d.per_bug,
		// diff-mode extras (absent on whole-tree projects)
		...(m.recall_by_distance
			? {
					recallByDistance: Object.fromEntries(
						Object.entries(m.recall_by_distance).map(([tier, v]) => [
							tier,
							{ bugs: v.bugs, mean: round(v.mean), min: round(v.min), max: round(v.max) }
						])
					)
				}
			: {}),
		...(m.out_of_diff_discovery ? { outOfDiff: round(m.out_of_diff_discovery.mean) } : {}),
		...(d.per_base_bug ? { perBaseBug: d.per_base_bug } : {})
	});
}

// tools = (provider, model) pairs that appear, in config order.
const tools = [];
const ids = new Set();
for (const key of providerOrder) {
	const pm = providerMeta[key];
	for (const model of Object.keys(pm.byModel)) {
		if (!seenPairs.has(`${key}/${model}`)) continue;
		const mm = pm.byModel[model];
		const id = toolIdOf(key, model);
		if (ids.has(id)) throw new Error(`duplicate tool id "${id}" — model names must slug uniquely`);
		ids.add(id);
		tools.push({
			id,
			model,
			modelLabel: mm.modelLabel,
			providerLabel: pm.label,
			kind: pm.kind,
			color: { light: mm.color, dark: mm.colorDark }
		});
	}
}
// any (provider, model) seen in results but not declared in config.models?
for (const pair of seenPairs) {
	const [prov, model] = pair.split('/');
	if (!providerMeta[prov]?.byModel[model])
		console.warn(`result model "${model}" is not in config providers.${prov}.models — using provider fallback colour`);
}

const seenProjects = new Set(configs.map((c) => c.project));
const projects = projectOrder
	.filter((p) => seenProjects.has(p))
	.map((p) => ({
		id: p,
		label: p,
		theme: projectTheme[p] ?? '',
		reviewMode: projectMode[p] ?? 'tree',
		bugs: bugsByProject[p] ?? [],
		...(baseBugsByProject[p]?.length ? { baseBugs: baseBugsByProject[p] } : {})
	}));

// real per-severity planted totals (never an even-split guess)
const allBugs = projects.flatMap((p) => p.bugs);
const plantedBySeverity = Object.fromEntries(
	SEVERITIES.map((s) => [s, allBugs.filter((b) => b.severity === s).length])
);

// ---- combined "overall": every project merged, recall split by severity -----
// Pooled counts across projects: found = sum of per-bug run-hits, possible =
// planted bugs of that severity × runs. Honest integers, denominator adapts to
// the real run count.
const severityCounts = (project, perBug, runs) => {
	const bugs = bugsByProject[project] ?? [];
	const out = {};
	for (const sev of SEVERITIES) {
		const idsForSev = bugs.filter((b) => b.severity === sev).map((b) => b.id);
		out[sev] = {
			found: idsForSev.reduce((s, id) => s + (perBug[id] ?? 0), 0),
			possible: idsForSev.length * runs
		};
	}
	return out;
};

const overallMap = new Map();
for (const c of configs) {
	const key = `${c.provider}|${c.model}|${c.effort}`;
	if (!overallMap.has(key)) overallMap.set(key, { ...c, rows: [] });
	overallMap.get(key).rows.push(c);
}
const overall = [...overallMap.values()].map((g) => {
	const bySeverity = {};
	for (const sev of SEVERITIES) {
		let found = 0;
		let possible = 0;
		for (const r of g.rows) {
			const c = severityCounts(r.project, r.perBug, r.runs)[sev];
			found += c.found;
			possible += c.possible;
		}
		bySeverity[sev] = { found, possible };
	}
	const costs = g.rows.map((r) => r.cost);
	const speeds = g.rows.map((r) => r.speedS);
	const speedsSeen = speeds.filter((s) => s != null);
	return {
		tool: g.tool,
		provider: g.provider,
		model: g.model,
		effort: g.effort,
		native: g.native,
		manual: g.manual,
		projects: g.rows.length,
		recall: round(mean(g.rows.map((r) => r.recall.mean)), 4),
		bySeverity,
		fp: round(mean(g.rows.map((r) => r.fp)), 2),
		cost: costs.some((c) => c == null) ? null : round(mean(costs), 4), // mean $/run (for scatters)
		costTotal: costs.some((c) => c == null) ? null : round(costs.reduce((s, c) => s + c, 0), 4), // one full pass, all projects
		bonusTotal: round(g.rows.reduce((s, r) => s + r.bonus, 0), 1),
		speedMean: speedsSeen.length ? Math.round(mean(speedsSeen)) : null, // mean s/run (per-review latency)
		// one full pass, all projects, serial — mirrors costTotal's rule:
		// any missing project makes the total unknowable, so null (never a partial sum)
		speedTotal: speeds.some((s) => s == null) ? null : Math.round(speeds.reduce((s, x) => s + x, 0))
	};
});
overall.sort((a, b) => b.recall - a.recall || (a.cost ?? 1e9) - (b.cost ?? 1e9));

// per-project configs sorted (project order, recall desc, cost asc)
const prorder = (p) => projectOrder.indexOf(p);
configs.sort(
	(a, b) =>
		prorder(a.project) - prorder(b.project) ||
		b.recall.mean - a.recall.mean ||
		(a.cost ?? 1e9) - (b.cost ?? 1e9)
);

// include any effort that appears in results but wasn't declared in config.
for (const c of configs) if (!effortOrder.includes(c.effort)) effortOrder.push(c.effort);

const bugCounts = projects.map((p) => p.bugs.length);
const data = {
	meta: {
		generatedFrom: 'harness/config.toml + harness/results',
		projects: projects.length,
		tools: tools.length,
		configs: configs.length,
		totalPlanted: allBugs.length,
		bugsPerProject: bugCounts.every((n) => n === bugCounts[0]) ? (bugCounts[0] ?? 0) : null,
		plantedBySeverity,
		runsDefault: cfg.run?.default_runs ?? 3
	},
	severities: SEVERITIES,
	effortOrder,
	tools,
	projects,
	configs,
	overall
};

mkdirSync(dirname(OUT), { recursive: true });
writeFileSync(OUT, JSON.stringify(data, null, 2) + '\n');

// ---- generated palette CSS: one --tool-<id> per model (light + dark) --------
const lightVars = tools.map((t) => `\t--tool-${t.id}: ${t.color.light};`).join('\n');
const darkVars = tools.map((t) => `\t--tool-${t.id}: ${t.color.dark};`).join('\n');
const css = `/* GENERATED from harness/config.toml by scripts/build-data.mjs — do not edit. */
:root {
${lightVars}
}
.dark {
${darkVars}
}
`;
mkdirSync(dirname(CSS), { recursive: true });
writeFileSync(CSS, css);

console.log(
	`wrote ${OUT}: ${tools.length} tools (models), ${projects.length} projects, ${configs.length} configs, ${overall.length} overall rows`
);
console.log(`wrote ${CSS}: ${tools.length} model hues × light/dark`);
