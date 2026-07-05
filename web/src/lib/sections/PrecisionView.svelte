<script lang="ts">
	import SectionHeader from '$lib/components/SectionHeader.svelte';
	import PrecisionScatter from '$lib/charts/PrecisionScatter.svelte';
	import { overall } from '$lib/benchmark';
</script>

{#if overall.length}
	<section id="precision" class="mx-auto max-w-4xl px-6 py-16">
		<SectionHeader
			kicker="Precision"
			title="Recall vs false positives"
			dek="The second axis. Overall recall against false positives per run — points on the left edge reported none. Hover a point for detail."
		/>
		<PrecisionScatter />
		<p class="mono mt-3 text-[11px] text-muted">measured · false positives = safe code wrongly flagged · axis truncated to show the band</p>
	</section>
{/if}
