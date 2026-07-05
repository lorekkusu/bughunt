<script lang="ts">
	import { paretoValue, tools } from '$lib/benchmark';
	import { toolColor } from '$lib/tools';
	import { reveal } from '$lib/actions/reveal';

	const W = 760;
	const H = 360;
	const m = { t: 18, r: 20, b: 44, l: 40 };
	const iw = W - m.l - m.r;
	const ih = H - m.t - m.b;

	const valuePoints = paretoValue;
	const costs = valuePoints.map((p) => p.cost);
	const recalls = valuePoints.map((p) => p.recall);
	// frontier = non-dominated, sorted by cost ascending
	const frontier = valuePoints.filter((p) => !p.dominated).slice().sort((a, b) => a.cost - b.cost);
	const xMax = Math.ceil(Math.max(...costs) * 10) / 10;
	const yMin = Math.max(0, Math.floor(Math.min(...recalls) * 10) / 10);
	const yMax = 1;

	const xOf = (c: number) => m.l + (c / xMax) * iw;
	const yOf = (r: number) => m.t + (1 - (r - yMin) / (yMax - yMin)) * ih;
	const frontierPath = frontier
		.map((p, i) => `${i ? 'L' : 'M'}${xOf(p.cost).toFixed(1)},${yOf(p.recall).toFixed(1)}`)
		.join(' ');

	const xTicks = (() => {
		const out: number[] = [];
		for (let v = 0; v <= xMax + 1e-9; v += 0.2) out.push(Math.round(v * 100) / 100);
		return out;
	})();
	const yTicks = (() => {
		const out: number[] = [];
		for (let v = yMin; v <= yMax + 1e-9; v += 0.05) out.push(Math.round(v * 100) / 100);
		return out;
	})();

	// legend = the models that appear, in tool order
	const legend = tools.filter((t) => valuePoints.some((p) => p.tool === t.id));

	let hover = $state<{ x: number; y: number; label: string; sub: string } | null>(null);
	let box: HTMLDivElement;
	function enter(e: MouseEvent, label: string, sub: string) {
		const c = box.getBoundingClientRect();
		const r = (e.currentTarget as SVGElement).getBoundingClientRect();
		hover = { x: r.left - c.left + r.width / 2, y: r.top - c.top, label, sub };
	}
</script>

<div class="relative reveal" bind:this={box} use:reveal>
	<svg viewBox="0 0 {W} {H}" class="w-full" role="img" aria-label="Recall versus estimated cost per run">
		{#each yTicks as t (t)}
			<line x1={m.l} x2={m.l + iw} y1={yOf(t)} y2={yOf(t)} stroke="var(--color-hairline)" stroke-width="1" />
			<text x={m.l - 6} y={yOf(t) + 3} text-anchor="end" class="mono" font-size="10" fill="var(--color-muted)">{Math.round(t * 100)}%</text>
		{/each}
		{#each xTicks as t (t)}
			<text x={xOf(t)} y={H - 22} text-anchor="middle" class="mono" font-size="10" fill="var(--color-muted)">${t.toFixed(2)}</text>
		{/each}
		<text x={m.l + iw / 2} y={H - 6} text-anchor="middle" class="mono" font-size="11" fill="var(--color-ink-2)">estimated cost / run</text>

		<!-- Pareto frontier: best recall for the cost -->
		<path d={frontierPath} fill="none" stroke="var(--color-ink-2)" stroke-width="1.5" stroke-dasharray="4 3" opacity="0.55" />

		{#each valuePoints as p (p.tool + p.effort)}
			<circle
				cx={xOf(p.cost)}
				cy={yOf(p.recall)}
				r={p.dominated ? 5 : 6.5}
				fill={toolColor(p.tool)}
				fill-opacity={p.dominated ? 0.3 : 0.95}
				stroke="var(--color-surface)"
				stroke-width="1.5"
				class="cursor-pointer"
				role="presentation"
				onmouseenter={(e) => enter(e, `${p.modelLabel}${p.effort !== 'default' ? '·' + p.effort : ''}`, `${Math.round(p.recall * 100)}% · $${p.cost.toFixed(2)}/run · ${p.providerLabel}`)}
				onmouseleave={() => (hover = null)}
			/>
		{/each}
	</svg>

	<div class="mt-2 flex flex-wrap gap-x-4 gap-y-1">
		{#each legend as t (t.id)}
			<span class="inline-flex items-center gap-1.5">
				<span class="inline-block h-2.5 w-2.5 rounded-[2px]" style="background: {toolColor(t.id)}"></span>
				<span class="mono text-[12px] text-ink-2">{t.modelLabel}</span>
			</span>
		{/each}
	</div>

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
