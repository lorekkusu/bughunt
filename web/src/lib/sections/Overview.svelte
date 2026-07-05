<script lang="ts">
	import SectionHeader from '$lib/components/SectionHeader.svelte';
	import OverviewMatrix from '$lib/components/OverviewMatrix.svelte';
	import { meta, severities } from '$lib/benchmark';

	const split = severities
		.map((s) => `${meta.plantedBySeverity[s]} ${s}`)
		.join(', ');
</script>

<section id="overall" class="mx-auto max-w-4xl px-6 py-16">
	<SectionHeader
		kicker="Overall"
		title={`All ${meta.projects} projects, combined`}
		dek={`Every project's planted bugs merged — ${meta.totalPlanted} in total (${split}). Each severity cell shows how many run-hits were found out of the possible total, pooled across the ${meta.projects} projects; the overall column is mean recall.`}
	/>
	<OverviewMatrix />
	<p class="mono mt-4 text-[11px] text-muted">
		measured · {meta.configs} configs × {meta.runsDefault} runs · generated from harness/config.toml + harness/results
	</p>
</section>
