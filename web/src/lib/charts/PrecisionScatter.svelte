<script lang="ts">
	import { overall, tools } from '$lib/benchmark';
	import { toolColor } from '$lib/tools';
	import { reveal } from '$lib/actions/reveal';

	const W = 760;
	const H = 340;
	const m = { t: 18, r: 20, b: 44, l: 40 };
	const iw = W - m.l - m.r;
	const ih = H - m.t - m.b;

	const recalls = overall.map((o) => o.recall);
	const xMax = Math.max(1, Math.ceil(Math.max(...overall.map((o) => o.fp)) * 2) / 2);
	const yMin = Math.max(0, Math.floor(Math.min(...recalls) * 10) / 10);
	const yMax = 1;

	const xOf = (fp: number) => m.l + (fp / xMax) * iw;
	const yOf = (r: number) => m.t + (1 - (r - yMin) / (yMax - yMin)) * ih;

	const xTicks = (() => {
		const out: number[] = [];
		for (let v = 0; v <= xMax + 1e-9; v += 0.5) out.push(Math.round(v * 10) / 10);
		return out;
	})();
	const yTicks = (() => {
		const out: number[] = [];
		for (let v = yMin; v <= yMax + 1e-9; v += 0.05) out.push(Math.round(v * 100) / 100);
		return out;
	})();

	const legend = tools.filter((t) => overall.some((o) => o.tool === t.id));

	let hover = $state<{ x: number; y: number; label: string; sub: string } | null>(null);
	let box: HTMLDivElement;
	function enter(e: MouseEvent, label: string, sub: string) {
		const c = box.getBoundingClientRect();
		const r = (e.currentTarget as SVGElement).getBoundingClientRect();
		hover = { x: r.left - c.left + r.width / 2, y: r.top - c.top, label, sub };
	}
</script>

<div class="relative reveal" bind:this={box} use:reveal>
	<svg viewBox="0 0 {W} {H}" class="w-full" role="img" aria-label="Recall versus false positives per run">
		{#each yTicks as t (t)}
			<line x1={m.l} x2={m.l + iw} y1={yOf(t)} y2={yOf(t)} stroke="var(--color-hairline)" stroke-width="1" />
			<text x={m.l - 6} y={yOf(t) + 3} text-anchor="end" class="mono" font-size="10" fill="var(--color-muted)">{Math.round(t * 100)}%</text>
		{/each}
		{#each xTicks as t (t)}
			<line x1={xOf(t)} x2={xOf(t)} y1={m.t} y2={m.t + ih} stroke="var(--color-hairline)" stroke-width={t === 0 ? 1.5 : 0.5} stroke-opacity={t === 0 ? 1 : 0.5} />
			<text x={xOf(t)} y={H - 22} text-anchor="middle" class="mono" font-size="10" fill="var(--color-muted)">{t.toFixed(1)}</text>
		{/each}
		<text x={m.l + iw / 2} y={H - 6} text-anchor="middle" class="mono" font-size="11" fill="var(--color-ink-2)">false positives / run</text>

		{#each overall as o (o.tool + o.effort)}
			<circle
				cx={xOf(o.fp)}
				cy={yOf(o.recall)}
				r="6"
				fill={toolColor(o.tool)}
				fill-opacity="0.85"
				stroke="var(--color-surface)"
				stroke-width="1.5"
				class="cursor-pointer"
				role="presentation"
				onmouseenter={(e) => enter(e, `${o.model}${o.effort !== 'default' ? '·' + o.effort : ''}`, `${Math.round(o.recall * 100)}% recall · ${o.fp.toFixed(1)} FP/run`)}
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
