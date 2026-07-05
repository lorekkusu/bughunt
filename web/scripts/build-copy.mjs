// Build a self-contained Markdown snapshot of the whole benchmark, for the
// "Copy for your AI" button. Derived from benchmark.json (numbers) + RESULTS.md
// (the vetted interpretation), so it never drifts from what the page shows.
// Emits src/lib/generated/copy.md. Run: `pnpm copy` (wired into build/dev).
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const DATA = join(here, '..', 'src', 'lib', 'data', 'benchmark.json');
const RESULTS = join(here, '..', '..', 'RESULTS.md');
const OUT = join(here, '..', 'src', 'lib', 'generated', 'copy.md');

const d = JSON.parse(readFileSync(DATA, 'utf-8'));
const results = readFileSync(RESULTS, 'utf-8').replace(/^#\s.*\n/, '').trim(); // drop H1

const toolLabel = Object.fromEntries(d.tools.map((t) => [t.id, t.modelLabel]));
const kindOf = Object.fromEntries(d.tools.map((t) => [t.id, t.kind]));
const label = (tool, effort) => {
	const base = toolLabel[tool] ?? tool;
	const tag = kindOf[tool] === 'native' ? ' (native)' : kindOf[tool] === 'manual' ? ' (manual)' : '';
	return (effort && effort !== 'default' ? `${base} · ${effort}` : base) + tag;
};
const pct = (x) => (x == null ? '—' : `${Math.round(x * 100)}%`);
const money = (x) => (x == null ? '—' : `$${x.toFixed(2)}`);
const secs = (x) => (x == null ? '—' : `${x}s`);

const L = [];
L.push('# bughunt — AI code-review benchmark (data snapshot)');
L.push('');
L.push(
	'An informal, open benchmark: each project hides a known set of planted bugs, every tool gets the same prompt, and findings are scored by an LLM-as-judge (Claude Opus). This is a snapshot for you to reason over.'
);
L.push('');
L.push(
	`**Caveats (please keep in mind):** small, fully-readable projects; a single LLM judge; one language (Python) so far; costs are API-equivalent list-price estimates, not billed spend; \`native\`/\`manual\` tools use their own prompt, so they are not directly comparable on the prompt axis. Treat this as a directional signal, not an authoritative ranking — results can shift as tools improve.`
);
L.push('');
const sev = d.severities.map((s) => `${d.meta.plantedBySeverity[s]} ${s}`).join(' / ');
L.push(
	`**Scope:** ${d.meta.tools} models, ${d.meta.projects} projects, ${d.meta.totalPlanted} planted bugs (${sev}), ${d.meta.runsDefault} runs per config.`
);
L.push('');

// ---- overall table ----------------------------------------------------------
L.push('## Overall — all projects combined');
L.push('');
L.push(
	'Severity cells are found / possible run-hits (planted bugs × runs, all projects). Overall = mean recall. bonus/$ are totals for one full pass; speed is mean s/run.'
);
L.push('');
const sevHead = d.severities.map((s) => s[0].toUpperCase() + s.slice(1)).join(' | ');
L.push(`| # | config | ${sevHead} | overall | FP | bonus | avg speed | total $ |`);
L.push(`|--:|--------|${d.severities.map(() => '---').join('|')}|---|---|---|---|---|`);
d.overall.forEach((o, i) => {
	const cells = d.severities.map((s) => `${o.bySeverity[s].found}/${o.bySeverity[s].possible}`).join(' | ');
	L.push(
		`| ${i + 1} | ${label(o.tool, o.effort)} | ${cells} | ${pct(o.recall)} | ${o.fp.toFixed(1)} | +${Math.round(o.bonusTotal)} | ${secs(o.speedMean)} | ${money(o.costTotal)} |`
	);
});
L.push('');

// ---- per-project leaderboards ----------------------------------------------
L.push('## Per-project leaderboards');
L.push('');
for (const p of d.projects) {
	const rows = d.configs
		.filter((c) => c.project === p.id)
		.slice()
		.sort((a, b) => b.recall.mean - a.recall.mean || (a.cost ?? 1e9) - (b.cost ?? 1e9));
	L.push(`### ${p.id} — ${p.theme}`);
	L.push('');
	L.push('| # | config | recall | FP | bonus | speed | $/run |');
	L.push('|--:|--------|-------:|---:|------:|------:|------:|');
	rows.forEach((c, i) => {
		L.push(
			`| ${i + 1} | ${label(c.tool, c.effort)} | ${pct(c.recall.mean)} | ${c.fp.toFixed(1)} | +${c.bonus.toFixed(1)} | ${secs(c.speedS)} | ${money(c.cost)} |`
		);
	});
	L.push('');
}

// ---- interpretation ---------------------------------------------------------
L.push('---');
L.push('');
L.push('## Interpretation (AI-generated — written by Claude from the data above, may change)');
L.push('');
L.push(results);
L.push('');
L.push('---');
L.push('');
L.push('Source: https://github.com/lorekkusu/bughunt · generated from harness/config.toml + harness/results.');
L.push('');
L.push(
	'You can paste this into an AI assistant and ask which tool / effort fits your use case, budget, and latency — or fork the repo, add your own projects, and run it yourself.'
);

mkdirSync(dirname(OUT), { recursive: true });
writeFileSync(OUT, L.join('\n') + '\n');
console.log(`wrote ${OUT}: ${L.length} lines`);
