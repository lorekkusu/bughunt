<script lang="ts">
	import { effortSeries, effortAxis } from '$lib/benchmark';
	import { toolColor } from '$lib/tools';
	import { reveal } from '$lib/actions/reveal';

	const W = 760;
	const H = 340;
	const m = { t: 18, r: 96, b: 34, l: 40 };
	const iw = W - m.l - m.r;
	const ih = H - m.t - m.b;

	const recalls = effortSeries.flatMap((s) => s.points.map((p) => p.recall));
	const yMin = Math.max(0, Math.floor(Math.min(...recalls) * 10) / 10);
	const yMax = 1;

	const xOf = (e: string) =>
		m.l + (effortAxis.length > 1 ? effortAxis.indexOf(e) / (effortAxis.length - 1) : 0.5) * iw;
	const yOf = (r: number) => m.t + (1 - (r - yMin) / (yMax - yMin)) * ih;
	const path = (pts: { effort: string; recall: number }[]) =>
		pts.map((p, i) => `${i ? 'L' : 'M'}${xOf(p.effort).toFixed(1)},${yOf(p.recall).toFixed(1)}`).join(' ');

	const yTicks = (() => {
		const out: number[] = [];
		for (let v = yMin; v <= yMax + 1e-9; v += 0.05) out.push(Math.round(v * 100) / 100);
		return out;
	})();

	let hover = $state<{ x: number; y: number; label: string; sub: string } | null>(null);
	let box: HTMLDivElement;
	function enter(e: MouseEvent, label: string, sub: string) {
		const c = box.getBoundingClientRect();
		const r = (e.currentTarget as SVGElement).getBoundingClientRect();
		hover = { x: r.left - c.left + r.width / 2, y: r.top - c.top, label, sub };
	}
</script>

<div class="relative reveal" bind:this={box} use:reveal>
	<svg viewBox="0 0 {W} {H}" class="w-full" role="img" aria-label="Recall versus reasoning effort">
		<!-- gridlines + y labels -->
		{#each yTicks as t (t)}
			<line x1={m.l} x2={m.l + iw} y1={yOf(t)} y2={yOf(t)} stroke="var(--color-hairline)" stroke-width="1" />
			<text x={m.l - 6} y={yOf(t) + 3} text-anchor="end" class="mono" font-size="10" fill="var(--color-muted)">
				{Math.round(t * 100)}%
			</text>
		{/each}
		<!-- x labels -->
		{#each effortAxis as e (e)}
			<text x={xOf(e)} y={H - 12} text-anchor="middle" class="mono" font-size="11" fill="var(--color-ink-2)">{e}</text>
		{/each}

		<!-- one line per model -->
		{#each effortSeries as s (s.tool)}
			<path d={path(s.points)} fill="none" stroke={toolColor(s.tool)} stroke-width="2" stroke-linejoin="round" />
			{#each s.points as p (p.effort)}
				<circle
					cx={xOf(p.effort)}
					cy={yOf(p.recall)}
					r="4.5"
					fill="var(--color-surface)"
					stroke={toolColor(s.tool)}
					stroke-width="2"
					class="cursor-pointer"
					role="presentation"
					onmouseenter={(e) => enter(e, `${s.modelLabel}·${p.effort}`, `${Math.round(p.recall * 100)}% recall · ${s.providerLabel}`)}
					onmouseleave={() => (hover = null)}
				/>
			{/each}
			<!-- endpoint label -->
			{@const last = s.points[s.points.length - 1]}
			<text
				x={xOf(last.effort) + 8}
				y={yOf(last.recall) + 3}
				class="mono"
				font-size="11"
				fill={toolColor(s.tool)}>{s.modelLabel}</text
			>
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
