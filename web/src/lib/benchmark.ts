import raw from './data/benchmark.json';
import type { Benchmark, Config, Project } from './types';

const data = raw as unknown as Benchmark;

export const meta = data.meta;
export const severities = data.severities;
export const effortOrder = data.effortOrder;
export const tools = data.tools;
export const projects = data.projects;
export const configs = data.configs as Config[];
export const overall = data.overall;
export const toolById = new Map(tools.map((t) => [t.id, t]));

/** Configs for one project, ranked by recall (desc) then cost (asc). */
export function leaderboard(projectId: string): Config[] {
	return configs
		.filter((c) => c.project === projectId)
		.slice()
		.sort(
			(a, b) => b.recall.mean - a.recall.mean || (a.cost ?? Infinity) - (b.cost ?? Infinity)
		);
}

export const leaderboards: { project: Project; rows: Config[] }[] = projects.map((p) => ({
	project: p,
	rows: leaderboard(p.id)
}));

/** Global cost range for the value-frontier scatter (models that report cost). */
export const costExtent = (() => {
	const cs = configs.map((c) => c.cost).filter((c): c is number => c != null);
	return { min: Math.min(...cs), max: Math.max(...cs) };
})();

/** Look up the (model) series for a config/overall row. */
export const toolFor = (id: string) => toolById.get(id);

/** Primary display for a config row: model label + effort (effort hidden when "default"). */
export const seriesLabel = (id: string, effort: string) => {
	const t = toolById.get(id);
	const m = t?.modelLabel ?? id;
	return effort && effort !== 'default' ? `${m}·${effort}` : m;
};

// ---- Diff-mode: recall by context distance ------------------------------------

/** Human definitions for the distance tiers (axis + tooltips). */
export const DISTANCE_DEFS: Record<string, string> = {
	D0: 'in the hunk',
	D1: 'modified file',
	D2: 'one-hop caller',
	D3: 'multi-hop'
};

/**
 * One decay curve per tool for a diff-mode project, taken at the tool's
 * best-recall config (leaderboard order = recall desc, cost asc, so the first
 * config seen per tool is its best). Color follows the tool, never the rank.
 */
export function distanceSeries(projectId: string) {
	const rows = leaderboard(projectId).filter((c) => c.recallByDistance);
	const seen = new Set<string>();
	const best: Config[] = [];
	for (const c of rows) {
		if (seen.has(c.tool)) continue;
		seen.add(c.tool);
		best.push(c);
	}
	const tiers = [...new Set(best.flatMap((c) => Object.keys(c.recallByDistance!)))].sort();
	const series = best.map((c) => {
		const t = toolById.get(c.tool);
		return {
			tool: c.tool,
			effort: c.effort,
			label: seriesLabel(c.tool, c.effort),
			providerLabel: t?.providerLabel ?? '',
			kind: t?.kind ?? 'model',
			runs: c.runs,
			points: tiers
				.filter((tier) => c.recallByDistance![tier])
				.map((tier) => ({ tier, ...c.recallByDistance![tier] }))
		};
	});
	return { tiers, series };
}

/** Scope-discipline facts across every config of a diff-mode project. */
export function diffDiscipline(projectId: string) {
	const rows = configs.filter((c) => c.project === projectId);
	return {
		configs: rows.length,
		runs: rows.reduce((s, c) => s + c.runs, 0),
		fpClean: rows.every((c) => c.fp === 0),
		outOfDiffZero: rows.every((c) => !c.outOfDiff)
	};
}

/** Recall vs effort — one line per model that ran more than one effort tier. */
const eIdx = (e: string) => effortOrder.indexOf(e);
export const effortSeries = tools
	.map((t) => {
		const rows = overall
			.filter((o) => o.tool === t.id)
			.slice()
			.sort((a, b) => eIdx(a.effort) - eIdx(b.effort));
		return {
			tool: t.id,
			modelLabel: t.modelLabel,
			providerLabel: t.providerLabel,
			kind: t.kind,
			points: rows.map((o) => ({ effort: o.effort, recall: o.recall, cost: o.cost }))
		};
	})
	.filter((s) => s.points.length >= 2);

/** The effort tiers actually used by the models plotted in the effort chart. */
export const effortAxis = effortOrder.filter((e) =>
	effortSeries.some((s) => s.points.some((p) => p.effort === e))
);

/** Recall vs cost — one point per config that reports a cost. */
export const valuePoints = overall
	.filter((o) => o.cost != null)
	.map((o) => {
		const t = toolById.get(o.tool);
		return {
			tool: o.tool,
			modelLabel: t?.modelLabel ?? o.model,
			providerLabel: t?.providerLabel ?? '',
			effort: o.effort,
			recall: o.recall,
			cost: o.cost as number,
			kind: t?.kind ?? 'model'
		};
	});

// ---------------------------------------------------------------------------
// Derived analyses. One shared rule: a config "finds" a bug if it caught it in
// a MAJORITY of its runs. findability = mean caught-fraction across runs.
// ---------------------------------------------------------------------------
const finds = (c: Config, id: string) => (c.perBug[id] ?? 0) >= Math.ceil(c.runs / 2);
const bugsOf = (projectId: string) => projects.find((p) => p.id === projectId)?.bugs ?? [];

/** Per planted bug (project, id): how findable it is, and by how many configs. */
export const bugStats = projects.flatMap((p) => {
	const pc = configs.filter((c) => c.project === p.id);
	return p.bugs.map((b) => {
		const fracs = pc.map((c) => (c.perBug[b.id] ?? 0) / c.runs);
		return {
			project: p.id,
			id: b.id,
			severity: b.severity,
			title: b.title,
			findability: fracs.reduce((s, x) => s + x, 0) / (fracs.length || 1),
			foundBy: pc.filter((c) => finds(c, b.id)).length,
			ofConfigs: pc.length
		};
	});
});
export const hardestBugs = bugStats.slice().sort((a, b) => a.findability - b.findability);

/** Distribution: how many of the N configs find each bug (0 = nobody). */
export const difficultyHistogram = (() => {
	const maxC = Math.max(0, ...bugStats.map((b) => b.ofConfigs));
	const bins = Array.from({ length: maxC + 1 }, (_, k) => ({ k, count: 0 }));
	for (const b of bugStats) bins[b.foundBy].count++;
	return bins;
})();

// ---- Ensemble: what a *set* of tools covers together --------------------------
type Cid = { key: string; tool: string; effort: string; set: Set<string> };
const byConfigId = (() => {
	const m = new Map<string, Cid>();
	for (const c of configs) {
		const key = `${c.tool}|${c.effort}`;
		if (!m.has(key)) m.set(key, { key, tool: c.tool, effort: c.effort, set: new Set() });
		const e = m.get(key)!;
		for (const b of bugsOf(c.project)) if (finds(c, b.id)) e.set.add(`${c.project}::${b.id}`);
	}
	return [...m.values()];
})();
const totalBugs = bugStats.length;
const diff = (s: Set<string>, covered: Set<string>) => {
	let n = 0;
	for (const x of s) if (!covered.has(x)) n++;
	return n;
};
export const ensemble = (() => {
	const best = byConfigId.reduce((a, b) => (b.set.size > a.set.size ? b : a), byConfigId[0]);
	const union = new Set<string>();
	byConfigId.forEach((e) => e.set.forEach((x) => union.add(x)));
	// greedy minimal team to reach the union
	const covered = new Set<string>();
	const pool = byConfigId.slice();
	const team: { tool: string; effort: string; added: number }[] = [];
	while (covered.size < union.size) {
		pool.sort((a, b) => diff(b.set, covered) - diff(a.set, covered));
		const pick = pool.shift();
		if (!pick || diff(pick.set, covered) === 0) break;
		const added = diff(pick.set, covered);
		pick.set.forEach((x) => covered.add(x));
		team.push({ tool: pick.tool, effort: pick.effort, added });
	}
	return {
		total: totalBugs,
		bestSingle: { tool: best.tool, effort: best.effort, n: best.set.size },
		unionN: union.size,
		neverN: totalBugs - union.size,
		team
	};
})();

/** Bugs that ONLY one model finds (any of its efforts) and no other model does. */
export const uniqueCatches = (() => {
	// union of found bugs per MODEL (across its efforts)
	const byTool = new Map<string, Set<string>>();
	for (const e of byConfigId) {
		if (!byTool.has(e.tool)) byTool.set(e.tool, new Set());
		const s = byTool.get(e.tool)!;
		e.set.forEach((x) => s.add(x));
	}
	const finders = new Map<string, string[]>(); // bug -> [tool...]
	byTool.forEach((set, tool) => set.forEach((bk) => (finders.get(bk) ?? finders.set(bk, []).get(bk)!).push(tool)));
	const out = new Map<string, string[]>();
	for (const [bk, ts] of finders) if (ts.length === 1) (out.get(ts[0]) ?? out.set(ts[0], []).get(ts[0])!).push(bk);
	return [...out.entries()].map(([tool, bugs]) => ({ tool, bugs })).sort((a, b) => b.bugs.length - a.bugs.length);
})();

// ---- Efficiency + Pareto on the value scatter --------------------------------
export const efficiency = overall
	.filter((o) => o.cost != null)
	.map((o) => ({
		tool: o.tool,
		effort: o.effort,
		recall: o.recall,
		recallPerDollar: o.recall / (o.cost as number),
		recallPerSec: o.speedMean ? o.recall / o.speedMean : null
	}))
	.sort((a, b) => b.recallPerDollar - a.recallPerDollar);

export const paretoValue = valuePoints.map((p) => ({
	...p,
	dominated: valuePoints.some(
		(q) => q !== p && q.recall >= p.recall && q.cost <= p.cost && (q.recall > p.recall || q.cost < p.cost)
	)
}));

// ---- Effort ROI: consecutive-tier deltas per multi-effort model --------------
export const effortRoi = tools
	.map((t) => {
		const rows = overall.filter((o) => o.tool === t.id).slice().sort((a, b) => eIdx(a.effort) - eIdx(b.effort));
		if (rows.length < 2) return null;
		const steps = rows.slice(1).map((b, i) => {
			const a = rows[i];
			return {
				from: a.effort,
				to: b.effort,
				dRecall: b.recall - a.recall,
				dCost: a.cost != null && b.cost != null ? (b.cost as number) - (a.cost as number) : null,
				dSpeed: a.speedMean != null && b.speedMean != null ? b.speedMean - a.speedMean : null
			};
		});
		return { tool: t.id, modelLabel: t.modelLabel, steps };
	})
	.filter((x): x is NonNullable<typeof x> => x != null);

/** Neutral scope facts for the hero — counts only, no verdict, all data-derived. */
export const scope = {
	tools: tools.length,
	projects: projects.length,
	configs: configs.length,
	totalPlanted: meta.totalPlanted,
	reviews: configs.reduce((s, c) => s + c.runs, 0)
};
