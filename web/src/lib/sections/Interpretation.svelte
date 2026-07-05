<script lang="ts">
	import results from '$lib/data/results.json';
	import LeaderboardPanel from '$lib/components/LeaderboardPanel.svelte';

	const blocks = results.blocks as Array<
		{ type: 'prose'; html: string } | { type: 'leaderboard'; project: string }
	>;
</script>

<section id="results" class="mx-auto max-w-4xl px-6 py-16">
	<div class="mb-10 flex gap-3 rounded-md border border-hairline bg-surface/50 p-4">
		<span class="text-[18px] leading-none" aria-hidden="true">🤖</span>
		<div class="flex flex-col gap-1">
			<span class="mono text-[12px] tracking-[0.12em] text-ink uppercase">AI-generated interpretation</span>
			<p class="text-[13px] leading-relaxed text-ink-2">
				The writeup below is <span class="text-ink">RESULTS.md</span>, rendered verbatim — it was
				written by Claude (an AI) from the measured data. The charts are the measurement; this reading
				is one informal interpretation and may change as tools improve and projects are added.
			</p>
		</div>
	</div>

	{#each blocks as block, i (i)}
		{#if block.type === 'leaderboard'}
			<LeaderboardPanel projectId={block.project} />
		{:else}
			<div class="results-prose">
				<!-- eslint-disable-next-line svelte/no-at-html-tags -->
				{@html block.html}
			</div>
		{/if}
	{/each}
</section>
