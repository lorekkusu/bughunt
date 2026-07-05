<script lang="ts">
	import SectionHeader from '$lib/components/SectionHeader.svelte';
	import PerBugHeatmap from '$lib/charts/PerBugHeatmap.svelte';
	import { projects } from '$lib/benchmark';
</script>

{#if projects.length}
	<section id="perbug" class="mx-auto max-w-4xl px-6 py-16">
		<SectionHeader
			kicker="Per bug"
			title="Which bugs get found"
			dek="Every planted bug (columns) against every configuration (rows), one project at a time. It shows the bugs the whole field misses, not just the totals."
		/>
		<PerBugHeatmap />
	</section>
{/if}
