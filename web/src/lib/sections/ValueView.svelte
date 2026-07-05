<script lang="ts">
	import SectionHeader from '$lib/components/SectionHeader.svelte';
	import ValueScatter from '$lib/charts/ValueScatter.svelte';
	import { valuePoints } from '$lib/benchmark';
</script>

{#if valuePoints.length}
	<section id="cost" class="mx-auto max-w-4xl px-6 py-16">
		<SectionHeader
			kicker="Cost"
			title="Recall vs cost"
			dek="Each configuration that reports a cost, plotted by estimated cost per run against overall recall. Tools that report no token usage (e.g. the manual and native reviewers) are omitted. Hover a point for detail."
		/>
		<ValueScatter />
		<p class="mono mt-3 text-[11px] text-muted">
			dashed line = Pareto frontier (most recall for the cost) · faded points are dominated · cost is an
			API-equivalent estimate, not billed spend
		</p>
	</section>
{/if}
