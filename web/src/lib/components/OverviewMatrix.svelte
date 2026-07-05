<script lang="ts">
	import { overall, severities, meta, toolFor, seriesLabel } from '$lib/benchmark';
	import { toolColor, kindBadge } from '$lib/tools';
	import ToolChip from './ToolChip.svelte';
	import type { Severity } from '$lib/types';

	const pct = (v: number | null) => (v == null ? '—' : `${Math.round(v * 100)}%`);

	// grid columns derived from the actual severity count (never a hardcoded 4):
	// config · severities · overall · FP · bonus · avg.speed · cost
	const cols = `minmax(12rem,1.6fr) repeat(${severities.length}, minmax(2.5rem,0.7fr)) minmax(3rem,0.8fr) 2.5rem 2.75rem 4rem 3.5rem`;

	const fpTone = (fp: number) =>
		fp === 0 ? 'var(--color-good)' : fp < 1 ? 'var(--color-warn)' : 'var(--color-critical)';
</script>

<div class="overflow-x-auto">
	<div class="min-w-[50rem]">
		<div
			class="mono grid items-end gap-1.5 border-b border-dotted border-hairline pb-2 text-[11px] tracking-wide text-muted"
			style="grid-template-columns: {cols}"
		>
			<span></span>
			{#each severities as sev (sev)}
				<span class="text-center capitalize">{sev}</span>
			{/each}
			<span class="text-center text-ink">overall</span>
			<span class="text-right">FP</span>
			<span class="text-right">bonus</span>
			<span class="text-right">avg.speed</span>
			<span class="text-right">$</span>
		</div>

		{#each overall as o, r (o.provider + o.model + o.effort)}
			{@const t = toolFor(o.tool)}
			<div
				class="mono tabular grid items-center gap-1.5 border-b border-hairline/50 py-1.5 text-[12px]"
				style="grid-template-columns: {cols}"
			>
				<div class="flex min-w-0 items-center gap-2">
					<span class="w-4 shrink-0 text-right text-[11px] text-muted">{r + 1}</span>
					<ToolChip tool={o.tool} primary={seriesLabel(o.tool, o.effort)} badge={t ? kindBadge(t.kind) : null} />
				</div>

				{#each severities as sev (sev)}
					{@const c = o.bySeverity[sev as Severity]}
					<span class="text-center text-ink-2" title="{sev}: {c.found} of {c.possible} run-hits found">
						{c.found}<span class="text-muted">/{c.possible}</span>
					</span>
				{/each}

				<span class="flex items-center justify-center gap-1.5 text-[13px] text-ink">
					<span class="inline-block h-2 w-2 rounded-[2px]" style="background: {toolColor(o.tool)}"></span>
					{pct(o.recall)}
				</span>

				<span class="text-right" style="color: {fpTone(o.fp)}" title="mean false positives / run">·{o.fp.toFixed(1)}</span>
				<span class="text-right text-ink-2" title="total extra real bugs found, all projects">+{Math.round(o.bonusTotal)}</span>
				<span class="text-right text-muted" title="mean seconds / run">{o.speedMean != null ? `${o.speedMean}s` : '—'}</span>
				<span class="text-right text-muted" title="total cost for one pass of all projects">{o.costTotal != null ? `$${o.costTotal.toFixed(2)}` : '—'}</span>
			</div>
		{/each}
	</div>
	<p class="mono mt-2 text-[11px] text-muted">
		severity cells: found / possible run-hits (planted × runs, all projects) · overall: mean recall · FP: mean/run · bonus &amp; $: totals for one full pass · speed: mean s/run
	</p>
</div>
