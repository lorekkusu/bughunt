<script lang="ts">
	import type { Config } from '$lib/types';
	import { toolColor, kindBadge } from '$lib/tools';
	import { toolFor, seriesLabel } from '$lib/benchmark';
	import ToolChip from './ToolChip.svelte';

	let {
		config,
		rank,
		grown = false
	}: { config: Config; rank: number; grown?: boolean } = $props();

	const pct = (x: number) => `${Math.round(x * 100)}%`;
	const t = $derived(toolFor(config.tool));
	const badge = $derived(t ? kindBadge(t.kind) : null);
	const fpTone = $derived(
		config.fp === 0 ? 'var(--color-good)' : config.fp < 1 ? 'var(--color-warn)' : 'var(--color-critical)'
	);
	const width = $derived(grown ? config.recall.mean * 100 : 0);
</script>

<div class="grid grid-cols-[1.25rem_12rem_1fr_auto] items-center gap-3 py-1.5">
	<span class="mono tabular text-right text-[12px] {rank === 1 ? 'text-ink' : 'text-muted'}">{rank}</span>

	<ToolChip tool={config.tool} primary={seriesLabel(config.tool, config.effort)} {badge} />

	<div class="relative h-[7px] overflow-hidden rounded-full" style="background: var(--color-seq-never)">
		<div
			class="absolute inset-y-0 left-0 rounded-full"
			style="width: {width}%; background: {toolColor(config.tool)}; transition: width 0.6s var(--ease)"
		></div>
	</div>

	<div class="mono tabular flex items-center gap-2.5 text-[13px] whitespace-nowrap">
		<span class="w-9 text-right text-ink" title="recall">{pct(config.recall.mean)}</span>
		<span class="w-9 text-right" style="color: {fpTone}" title="false positives / run">·{config.fp.toFixed(1)}</span>
		<span class="w-9 text-right text-ink-2" title="bonus — extra real bugs found">+{config.bonus.toFixed(1)}</span>
		<span class="w-11 text-right text-muted" title="mean seconds / run">{config.speedS != null ? `${config.speedS}s` : '—'}</span>
		<span class="w-12 text-right text-muted" title="est. cost / run">{config.cost != null ? `$${config.cost.toFixed(2)}` : '—'}</span>
	</div>
</div>
