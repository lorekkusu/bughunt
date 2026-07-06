<script lang="ts">
	import { distanceSeries, diffDiscipline, DISTANCE_DEFS, projects } from '$lib/benchmark';
	import { toolColor, kindBadge } from '$lib/tools';
	import { reveal } from '$lib/actions/reveal';

	let { projectId }: { projectId: string } = $props();

	const project = $derived(projects.find((p) => p.id === projectId));
	const data = $derived(distanceSeries(projectId));
	const discipline = $derived(diffDiscipline(projectId));

	const W = 760;
	const H = 380;
	const m = { t: 18, r: 148, b: 46, l: 40 };
	const iw = W - m.l - m.r;
	const ih = H - m.t - m.b;

	const xOf = (tier: string) => {
		const tiers = data.tiers;
		return m.l + (tiers.length > 1 ? tiers.indexOf(tier) / (tiers.length - 1) : 0.5) * iw;
	};
	const yOf = (r: number) => m.t + (1 - r) * ih;
	const path = (pts: { tier: string; mean: number }[]) =>
		pts.map((p, i) => `${i ? 'L' : 'M'}${xOf(p.tier).toFixed(1)},${yOf(p.mean).toFixed(1)}`).join(' ');

	const yTicks = [0, 0.25, 0.5, 0.75, 1];

	// End labels: nudge apart vertically so identical endpoints (e.g. two tools
	// tied at the same D3 recall) never collide.
	const endLabels = $derived.by(() => {
		const MIN_GAP = 14;
		const raw = data.series
			.map((s) => {
				const last = s.points[s.points.length - 1];
				return { tool: s.tool, label: s.label, y: yOf(last.mean) };
			})
			.sort((a, b) => a.y - b.y);
		for (let i = 1; i < raw.length; i++)
			if (raw[i].y - raw[i - 1].y < MIN_GAP) raw[i].y = raw[i - 1].y + MIN_GAP;
		return raw;
	});

	const dash = (kind: string) => (kind === 'model' ? undefined : '7 4');

	// per-tier planted counts, straight from the data (footer disclosure)
	const bugsPerTier = $derived.by(() => {
		const counts = new Set(data.series.flatMap((s) => s.points.map((p) => p.bugs)));
		return counts.size === 1 ? [...counts][0] : null;
	});

	let hover = $state<{ x: number; y: number; label: string; sub: string } | null>(null);
	let box: HTMLDivElement;
	function enter(e: MouseEvent, label: string, sub: string) {
		const c = box.getBoundingClientRect();
		const r = (e.currentTarget as SVGElement).getBoundingClientRect();
		hover = { x: r.left - c.left + r.width / 2, y: r.top - c.top, label, sub };
	}
</script>

{#if project && data.series.length}
	<figure class="my-8 rounded-md border border-hairline bg-surface/40 p-5">
		<figcaption
			class="mb-3 flex flex-wrap items-baseline justify-between gap-2 border-b border-dotted border-hairline pb-2"
		>
			<span class="mono text-[14px] text-ink">{project.label} · recall by context distance</span>
			<span class="mono text-[11px] text-muted">best config per tool · dashed = purpose-built reviewer</span>
		</figcaption>

		<!-- legend (identity is never color-alone; dash key doubles as kind badge) -->
		<div class="mono mb-2 flex flex-wrap gap-x-4 gap-y-1 text-[11px]">
			{#each data.series as s (s.tool)}
				<span class="flex items-center gap-1.5 text-ink-2">
					<svg width="22" height="8" aria-hidden="true">
						<line
							x1="1" y1="4" x2="21" y2="4"
							stroke={toolColor(s.tool)}
							stroke-width="2"
							stroke-dasharray={dash(s.kind)}
						/>
					</svg>
					{s.label}{#if kindBadge(s.kind as never)}<span class="rounded-[2px] border border-hairline px-1 text-[9px] text-muted">{kindBadge(s.kind as never)}</span>{/if}
				</span>
			{/each}
		</div>

		<div class="relative reveal" bind:this={box} use:reveal>
			<svg viewBox="0 0 {W} {H}" class="w-full" role="img" aria-label="Recall by context distance, one line per tool">
				{#each yTicks as t (t)}
					<line x1={m.l} x2={m.l + iw} y1={yOf(t)} y2={yOf(t)} stroke="var(--color-hairline)" stroke-width="1" />
					<text x={m.l - 6} y={yOf(t) + 3} text-anchor="end" class="mono" font-size="10" fill="var(--color-muted)">
						{Math.round(t * 100)}%
					</text>
				{/each}

				{#each data.tiers as tier (tier)}
					<text x={xOf(tier)} y={H - 26} text-anchor="middle" class="mono" font-size="11" fill="var(--color-ink-2)">{tier}</text>
					<text x={xOf(tier)} y={H - 12} text-anchor="middle" class="mono" font-size="9" fill="var(--color-muted)">{DISTANCE_DEFS[tier] ?? ''}</text>
				{/each}

				{#each data.series as s (s.tool)}
					<path
						d={path(s.points)}
						fill="none"
						stroke={toolColor(s.tool)}
						stroke-width="2"
						stroke-linejoin="round"
						stroke-dasharray={dash(s.kind)}
					/>
					{#each s.points as p (p.tier)}
						<circle
							cx={xOf(p.tier)}
							cy={yOf(p.mean)}
							r="4.5"
							fill="var(--color-surface)"
							stroke={toolColor(s.tool)}
							stroke-width="2"
							class="cursor-pointer"
							role="presentation"
							onmouseenter={(e) =>
								enter(
									e,
									`${p.tier} · ${s.label}`,
									`${Math.round(p.mean * 100)}% recall · ${p.bugs} bugs × ${s.runs} runs · ${DISTANCE_DEFS[p.tier] ?? ''}`
								)}
							onmouseleave={() => (hover = null)}
						/>
					{/each}
				{/each}

				{#each endLabels as l (l.tool)}
					<text x={m.l + iw + 10} y={l.y + 3} class="mono" font-size="11" fill={toolColor(l.tool)}>{l.label}</text>
				{/each}
			</svg>

			{#if hover}
				<div
					class="pointer-events-none absolute z-10 -translate-x-1/2 -translate-y-full rounded-sm border border-hairline bg-raised px-2 py-1 whitespace-nowrap shadow-sm"
					style="left: {hover.x}px; top: {hover.y - 6}px"
				>
					<div class="mono text-[12px] text-ink">{hover.label}</div>
					<div class="mono text-[11px] text-muted">{hover.sub}</div>
				</div>
			{/if}
		</div>

		<p class="mt-3 text-[13px] text-ink-2">
			Everyone reads the hunk; the field separates where the evidence leaves the file.
		</p>
		<p class="mono mt-1 text-[11px] text-muted">
			{data.tiers.map((t) => `${t} ${DISTANCE_DEFS[t] ?? ''}`).join(' · ')}{bugsPerTier ? ` · ${bugsPerTier} bugs per tier` : ''}
			{#if discipline.fpClean && discipline.outOfDiffZero}
				· scope discipline: {discipline.runs}/{discipline.runs} runs in-diff, 0.0 FP held, off-path tripwire untouched
			{/if}
		</p>
	</figure>
{/if}
