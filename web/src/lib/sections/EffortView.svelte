<script lang="ts">
	import SectionHeader from '$lib/components/SectionHeader.svelte';
	import EffortCurve from '$lib/charts/EffortCurve.svelte';
	import { effortSeries } from '$lib/benchmark';
</script>

{#if effortSeries.length}
	<section id="effort" class="mx-auto max-w-4xl px-6 py-16">
		<SectionHeader
			kicker="Effort"
			title="Recall vs reasoning effort"
			dek="For each model that ran more than one effort tier, overall recall from its lowest setting to its highest. Hover a point for detail."
		/>
		<EffortCurve />
		<p class="mono mt-3 text-[11px] text-muted">
			measured · overall recall across all projects · axis truncated to show the band
		</p>
	</section>
{/if}
