<script lang="ts">
	import StatTile from '$lib/components/StatTile.svelte';
	import { scope, meta, severities } from '$lib/benchmark';

	const split = severities.map((s) => `${meta.plantedBySeverity[s]} ${s}`).join(' / ');
</script>

<section class="mx-auto max-w-4xl px-6 pt-24 pb-16 sm:pt-32">
	<div class="mono mb-6 text-[12px] tracking-[0.2em] text-muted uppercase">
		bughunt · an informal, honest benchmark
	</div>

	<h1 class="max-w-4xl text-[clamp(2rem,5.5vw,3.75rem)] leading-[1.08] font-semibold tracking-tight">
		We plant known bugs in real code, then measure<br class="hidden sm:block" />
		what AI code reviewers actually catch.
	</h1>

	<p class="mt-7 max-w-2xl text-[16px] leading-relaxed text-ink-2">
		Across {meta.projects} projects we plant <span class="mono">{meta.totalPlanted}</span> bugs
		— <span class="mono">{split}</span> — plus safe-but-suspicious noise. Every tool gets the same
		prompt; findings are scored by an LLM judge, over <span class="mono">{meta.runsDefault} runs</span>.
		It's an informal one-person experiment, so treat it as a directional signal — the numbers can
		shift as tools improve and as more projects are added.
	</p>

	<div class="mt-14 grid grid-cols-2 gap-x-8 gap-y-10 border-t border-hairline pt-10 sm:grid-cols-4">
		<StatTile value={scope.tools} label="models" note="under test" />
		<StatTile value={scope.projects} label="projects" note="different domains" />
		<StatTile value={scope.totalPlanted} label="planted bugs" note="across all projects" />
		<StatTile value={scope.reviews} label="reviews" note="scored by the judge" />
	</div>
</section>
