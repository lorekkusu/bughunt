<script lang="ts">
	import SectionHeader from '$lib/components/SectionHeader.svelte';
	import StatTile from '$lib/components/StatTile.svelte';
	import { ensemble, uniqueCatches, toolFor, seriesLabel } from '$lib/benchmark';
	import { toolColor } from '$lib/tools';

	const total = ensemble.total;
	const bestPct = (ensemble.bestSingle.n / total) * 100;
	const unionPct = (ensemble.unionN / total) * 100;
	const bestLabel = seriesLabel(ensemble.bestSingle.tool, ensemble.bestSingle.effort);
	const unique = uniqueCatches.filter((u) => u.bugs.length > 0);
</script>

<section id="ensemble" class="mx-auto max-w-4xl px-6 py-16">
	<SectionHeader
		kicker="Ensemble"
		title="What if you ran all of them?"
		dek={`Combining tools is a different question from ranking them. Counting a bug as found when a config catches it in a majority of runs, across all ${total} planted bugs:`}
	/>

	<div class="grid grid-cols-1 gap-x-8 gap-y-10 border-t border-hairline pt-10 sm:grid-cols-3">
		<StatTile value={bestPct} suffix="%" label="best single tool" note={`${bestLabel} — ${ensemble.bestSingle.n}/${total}`} />
		<StatTile value={unionPct} suffix="%" label="all tools combined" note={`${ensemble.unionN}/${total} — the union of every catch`} />
		<StatTile
			value={ensemble.neverN}
			label={ensemble.neverN === 1 ? 'bug nobody finds' : 'bugs nobody finds'}
			tone={ensemble.neverN ? 'critical' : 'good'}
			note="not caught by any config"
		/>
	</div>

	<!-- minimal team -->
	<div class="mt-14">
		<div class="mono mb-3 text-[12px] text-muted">smallest set of configs that reaches that combined coverage</div>
		<div class="flex flex-wrap items-center gap-2">
			{#each ensemble.team as m, i (m.tool + m.effort)}
				{#if i > 0}<span class="mono text-muted">+</span>{/if}
				<span class="inline-flex items-center gap-1.5 rounded-sm border border-hairline px-2 py-1">
					<span class="inline-block h-2.5 w-2.5 rounded-[2px]" style="background: {toolColor(m.tool)}"></span>
					<span class="mono text-[13px] text-ink">{seriesLabel(m.tool, m.effort)}</span>
					<span class="mono text-[11px] text-muted">+{m.added}</span>
				</span>
			{/each}
		</div>
	</div>

	<!-- unique catches -->
	{#if unique.length}
		<div class="mt-12">
			<div class="mono mb-3 text-[12px] text-muted">bugs only one model finds (nobody else does)</div>
			<div class="flex flex-col gap-1.5">
				{#each unique as u (u.tool)}
					<div class="flex items-baseline gap-2">
						<span class="inline-block h-2.5 w-2.5 shrink-0 translate-y-[2px] rounded-[2px]" style="background: {toolColor(u.tool)}"></span>
						<span class="mono w-32 shrink-0 text-[13px] text-ink">{toolFor(u.tool)?.modelLabel ?? u.tool}</span>
						<span class="mono text-[12px] text-ink-2">{u.bugs.length} unique</span>
						<span class="mono truncate text-[11px] text-muted">{u.bugs.map((b) => b.split('::')[1] + ' (' + b.split('::')[0].replace('python-', '') + ')').join(' · ')}</span>
					</div>
				{/each}
			</div>
		</div>
	{/if}
</section>
