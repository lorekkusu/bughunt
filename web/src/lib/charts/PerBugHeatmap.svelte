<script lang="ts">
	import { projects, leaderboard, toolFor, seriesLabel } from '$lib/benchmark';
	import { toolColor, kindBadge, SEVERITY_STATUS } from '$lib/tools';
	import ToolChip from '$lib/components/ToolChip.svelte';
	import type { Config } from '$lib/types';

	let selected = $state(projects[0]?.id ?? '');
	const project = $derived(projects.find((p) => p.id === selected) ?? projects[0]);
	const rows = $derived(leaderboard(selected));
	const cols = $derived(`minmax(10rem,auto) repeat(${project?.bugs.length ?? 0}, minmax(0,1fr))`);

	const glyph = (n: number, runs: number) => (n >= runs ? '✅' : n <= 0 ? '❌' : '⚠️');

	let hover = $state<{ x: number; y: number; label: string; sub: string } | null>(null);
	let box: HTMLDivElement;
	function enter(e: MouseEvent, label: string, sub: string) {
		const c = box.getBoundingClientRect();
		const r = (e.currentTarget as HTMLElement).getBoundingClientRect();
		hover = { x: r.left - c.left + r.width / 2, y: r.top - c.top, label, sub };
	}
</script>

<div class="relative" bind:this={box}>
	<!-- project tabs -->
	<div class="mono mb-4 flex flex-wrap gap-1 text-[12px]">
		{#each projects as p (p.id)}
			<button
				type="button"
				onclick={() => (selected = p.id)}
				class="rounded-sm border px-2.5 py-1 transition-colors {selected === p.id
					? 'border-hairline bg-surface text-ink'
					: 'border-transparent text-muted hover:text-ink-2'}"
			>
				{p.label}
			</button>
		{/each}
	</div>

	{#if project}
		<div class="overflow-x-auto">
			<div class="min-w-[42rem]">
				<!-- header: bug ids -->
				<div class="grid items-end gap-0.5 border-b border-dotted border-hairline pb-1.5" style="grid-template-columns: {cols}">
					<span class="mono text-[11px] text-muted">config \\ bug</span>
					{#each project.bugs as b (b.id)}
						<span class="flex flex-col items-center gap-0.5" title="{b.severity} — {b.title}">
							<span class="inline-block h-1.5 w-1.5 rounded-full" style="background: {SEVERITY_STATUS[b.severity]}"></span>
							<span class="mono text-[10px] text-ink-2">{b.id}</span>
						</span>
					{/each}
				</div>

				<!-- one row per config -->
				{#each rows as c (c.provider + c.model + c.effort)}
					{@const t = toolFor(c.tool)}
					<div class="grid items-center gap-0.5 border-b border-hairline/40 py-1" style="grid-template-columns: {cols}">
						<div class="flex items-center gap-2 pr-2">
							<span class="inline-block h-2 w-2 shrink-0 rounded-[2px]" style="background: {toolColor(c.tool)}"></span>
							<span class="mono truncate text-[12px] text-ink">{seriesLabel(c.tool, c.effort)}</span>
							{#if t && kindBadge(t.kind)}
								<span class="mono rounded-[2px] border border-hairline px-1 text-[9px] text-muted">{kindBadge(t.kind)}</span>
							{/if}
						</div>
						{#each project.bugs as b (b.id)}
							{@const n = c.perBug[b.id] ?? 0}
							<span
								class="flex cursor-default items-center justify-center text-[13px] leading-none"
								role="presentation"
								onmouseenter={(e) => enter(e, `${b.id} · ${seriesLabel(c.tool, c.effort)}`, `found ${n}/${c.runs} runs — ${b.title}`)}
								onmouseleave={() => (hover = null)}
							>
								{glyph(n, c.runs)}
							</span>
						{/each}
					</div>
				{/each}
			</div>
		</div>
		<p class="mono mt-3 text-[11px] text-muted">
			✅ found every run · ⚠️ some runs · ❌ never · rows ranked by recall · hover a cell for the bug
		</p>
	{/if}

	{#if hover}
		<div
			class="pointer-events-none absolute z-10 max-w-xs -translate-x-1/2 -translate-y-full rounded-sm border border-hairline bg-raised px-2 py-1 shadow-sm"
			style="left: {hover.x}px; top: {hover.y - 6}px"
		>
			<div class="mono text-[12px] text-ink">{hover.label}</div>
			<div class="text-[11px] text-muted">{hover.sub}</div>
		</div>
	{/if}
</div>
