<script lang="ts">
	import LeaderboardRow from './LeaderboardRow.svelte';
	import { leaderboard, projects } from '$lib/benchmark';

	let { projectId }: { projectId: string } = $props();

	const project = $derived(projects.find((p) => p.id === projectId));
	const rows = $derived(leaderboard(projectId));

	const reduce =
		typeof matchMedia !== 'undefined' && matchMedia('(prefers-reduced-motion: reduce)').matches;
	let grown = $state(reduce);
	let el: HTMLElement;

	$effect(() => {
		if (grown || !el) return;
		const io = new IntersectionObserver(
			(entries) => {
				if (entries[0].isIntersecting) {
					grown = true;
					io.disconnect();
				}
			},
			{ threshold: 0.25 }
		);
		io.observe(el);
		return () => io.disconnect();
	});
</script>

{#if project}
	<figure bind:this={el} class="my-8 rounded-md border border-hairline bg-surface/40 p-5">
		<figcaption
			class="mb-3 flex items-baseline justify-between border-b border-dotted border-hairline pb-2"
		>
			<span class="mono text-[14px] text-ink">{project.label}</span>
			<span class="mono text-[11px] text-muted">recall · FP · bonus · speed · $/run{rows[0] ? ` · n=${rows[0].runs}` : ''}</span>
		</figcaption>
		<div class="overflow-x-auto">
			<div class="flex min-w-[32rem] flex-col">
				{#each rows as row, i (row.provider + row.model + row.effort)}
					<LeaderboardRow config={row} rank={i + 1} {grown} />
				{/each}
			</div>
		</div>
	</figure>
{/if}
