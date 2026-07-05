<script lang="ts">
	import SectionHeader from '$lib/components/SectionHeader.svelte';
	import { hardestBugs, difficultyHistogram, meta } from '$lib/benchmark';
	import { SEVERITY_STATUS } from '$lib/tools';
	import { reveal } from '$lib/actions/reveal';

	const top = hardestBugs.slice(0, 10);
	const maxBin = Math.max(...difficultyHistogram.map((b) => b.count));
	const nConfigs = difficultyHistogram.length - 1;
</script>

<section id="hardest" class="mx-auto max-w-4xl px-6 py-16">
	<SectionHeader
		kicker="Difficulty"
		title="Which bugs are hard for AI"
		dek={`Flip the axis: score the ${meta.totalPlanted} planted bugs by how findable they are across every configuration. A bug is "found" by a config if it caught it in a majority of runs.`}
	/>

	<!-- distribution: how many configs find each bug -->
	<div class="mb-12">
		<div class="mono mb-3 text-[12px] text-muted">bugs, by how many of the {nConfigs} configs find them</div>
		<div class="flex items-end gap-1.5" use:reveal>
			{#each difficultyHistogram as b (b.k)}
				<div class="flex flex-1 flex-col items-center gap-1">
					<span class="mono text-[11px] {b.count ? 'text-ink-2' : 'text-muted'}">{b.count || ''}</span>
					<div
						class="w-full rounded-t-[2px]"
						style="height: {b.count ? Math.max(4, (b.count / maxBin) * 120) : 1}px;
							background: {b.k === 0 ? 'var(--color-critical)' : b.k === nConfigs ? 'var(--color-good)' : 'var(--color-seq-some)'}"
						title="{b.count} bugs found by {b.k} of {nConfigs} configs"
					></div>
					<span class="mono text-[10px] text-muted">{b.k}</span>
				</div>
			{/each}
		</div>
		<div class="mono mt-2 flex justify-between text-[11px] text-muted">
			<span>0 = found by nobody</span>
			<span>{nConfigs} = found by everyone</span>
		</div>
	</div>

	<!-- the hardest, ranked -->
	<div class="mono mb-3 text-[12px] text-muted">the {top.length} hardest</div>
	<div class="flex flex-col">
		{#each top as b (b.project + b.id)}
			<div class="grid grid-cols-[7rem_1fr_3rem_3.5rem] items-center gap-3 border-b border-hairline/50 py-2">
				<span class="mono flex items-center gap-1.5 text-[12px] text-ink-2">
					<span class="inline-block h-1.5 w-1.5 rounded-full" style="background: {SEVERITY_STATUS[b.severity]}"></span>
					{b.id}
				</span>
				<span class="truncate text-[13px] text-ink" title="{b.project} — {b.title}">{b.title}</span>
				<span class="mono tabular text-right text-[13px] text-ink">{Math.round(b.findability * 100)}%</span>
				<span class="mono tabular text-right text-[12px] text-muted">{b.foundBy}/{b.ofConfigs}</span>
			</div>
		{/each}
	</div>
	<p class="mono mt-3 text-[11px] text-muted">% = mean caught-fraction across all configs · n/m = configs that found it (majority of runs)</p>
</section>
