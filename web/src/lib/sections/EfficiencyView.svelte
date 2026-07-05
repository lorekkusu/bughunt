<script lang="ts">
	import SectionHeader from '$lib/components/SectionHeader.svelte';
	import { efficiency, seriesLabel } from '$lib/benchmark';
	import { toolColor } from '$lib/tools';
	import { reveal } from '$lib/actions/reveal';

	const max = Math.max(...efficiency.map((e) => e.recallPerDollar));
	const rows = efficiency.slice(0, 10);
</script>

{#if rows.length}
	<section id="efficiency" class="mx-auto max-w-4xl px-6 py-16">
		<SectionHeader
			kicker="Efficiency"
			title="Recall per dollar"
			dek="Overall recall divided by estimated cost per run — how much bug-finding each dollar buys. Tools with no cost reported are omitted."
		/>
		<div class="flex flex-col gap-1.5" use:reveal>
			{#each rows as e, i (e.tool + e.effort)}
				<div class="grid grid-cols-[1.5rem_11rem_1fr_5rem] items-center gap-3">
					<span class="mono tabular text-right text-[12px] text-muted">{i + 1}</span>
					<span class="mono flex items-center gap-2 text-[13px] text-ink">
						<span class="inline-block h-2.5 w-2.5 rounded-[2px]" style="background: {toolColor(e.tool)}"></span>
						{seriesLabel(e.tool, e.effort)}
					</span>
					<div class="h-2 overflow-hidden rounded-full" style="background: var(--color-seq-never)">
						<div class="h-full rounded-full" style="width: {(e.recallPerDollar / max) * 100}%; background: {toolColor(e.tool)}"></div>
					</div>
					<span class="mono tabular text-right text-[12px] text-ink-2" title="recall per $ / run">{e.recallPerDollar.toFixed(2)}</span>
				</div>
			{/each}
		</div>
		<p class="mono mt-3 text-[11px] text-muted">bar = recall ÷ $/run (higher is more bug-finding per dollar)</p>
	</section>
{/if}
