// Render RESULTS.md (the vetted, human-approved interpretation) into ordered
// blocks: verbatim prose (as HTML) interleaved with `leaderboard` placeholders
// where each project's static table was — the site swaps those for the
// interactive chart. The prose is never rewritten here; it is rendered as-is.
// Run: `pnpm results` (wired into `pnpm build`).
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { marked } from 'marked';

const here = dirname(fileURLToPath(import.meta.url));
const SRC = join(here, '..', '..', 'RESULTS.md');
const OUT = join(here, '..', 'src', 'lib', 'data', 'results.json');
const DATA = join(here, '..', 'src', 'lib', 'data', 'benchmark.json');

// Known project ids (build-data.mjs runs first) — a project section is any H2
// whose backticked token is a real project. This tolerates heading-format drift
// (dash type, "Project N", ":") and never mis-attributes a chart.
let projectIds = new Set();
let diffProjects = new Set();
try {
	const bench = JSON.parse(readFileSync(DATA, 'utf-8'));
	projectIds = new Set(bench.projects.map((p) => p.id));
	diffProjects = new Set(bench.projects.filter((p) => p.reviewMode === 'diff').map((p) => p.id));
} catch {
	console.warn('build-results: benchmark.json not found — run build-data first; project charts may be skipped');
}

const md = readFileSync(SRC, 'utf-8');
const lines = md.split('\n');

const blocks = [];
let buf = [];
let currentProject = null; // set on a project H2, reset on any other H2
let sawTable = false; // only the FIRST table in a project section becomes a chart
let droppedTitle = false;

const flush = () => {
	const text = buf.join('\n').trim();
	if (text) blocks.push({ type: 'prose', html: marked.parse(text) });
	buf = [];
};

const isRow = (l) => /^\s*\|.*\|\s*$/.test(l);
const isSep = (l) => /^\s*\|[\s:|-]+\|\s*$/.test(l);

for (let i = 0; i < lines.length; ) {
	const line = lines[i];

	// Drop the top-level H1 (the hero already brands the page).
	if (!droppedTitle && /^#\s+/.test(line)) {
		droppedTitle = true;
		i++;
		continue;
	}

	// Any H2 (##) — a project section if its backticked token is a known project.
	if (/^##\s+/.test(line)) {
		const tick = line.match(/`([^`]+)`/);
		if (tick && projectIds.has(tick[1])) {
			currentProject = tick[1];
			sawTable = false;
		} else {
			currentProject = null; // leave a non-project section (never mis-attribute)
		}
		buf.push(line);
		i++;
		continue;
	}

	// The first pipe table inside a project section is that project's leaderboard;
	// replace it with a chart. Any other table renders normally as prose.
	if (isRow(line) && i + 1 < lines.length && isSep(lines[i + 1])) {
		if (currentProject && !sawTable) {
			flush();
			blocks.push({ type: 'leaderboard', project: currentProject });
			// diff-mode projects get the distance-decay chart right after the board
			if (diffProjects.has(currentProject))
				blocks.push({ type: 'distance', project: currentProject });
			sawTable = true;
			while (i < lines.length && isRow(lines[i])) i++;
			continue;
		}
		// fall through: keep this table as prose
	}

	buf.push(line);
	i++;
}
flush();

mkdirSync(dirname(OUT), { recursive: true });
writeFileSync(OUT, JSON.stringify({ blocks }, null, 2) + '\n');
const charts = blocks.filter((b) => b.type === 'leaderboard').length;
console.log(`wrote ${OUT}: ${blocks.length} blocks (${charts} inline leaderboards)`);
