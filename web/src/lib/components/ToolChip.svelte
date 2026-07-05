<script lang="ts">
	import type { ToolId } from '$lib/types';
	import { toolColor } from '$lib/tools';

	let {
		tool,
		primary,
		badge = null,
		size = 'sm'
	}: {
		tool: ToolId;
		primary: string;
		badge?: string | null;
		size?: 'sm' | 'md';
	} = $props();
</script>

<span class="inline-flex items-center gap-1.5 whitespace-nowrap">
	<span
		class="inline-block rounded-[2px] {size === 'md' ? 'h-3 w-3' : 'h-2.5 w-2.5'}"
		style="background: {toolColor(tool)}"
		aria-hidden="true"
	></span>
	<span class="mono {size === 'md' ? 'text-[14px]' : 'text-[13px]'} text-ink">{primary}</span>
	{#if badge}
		<span class="mono rounded-[2px] border border-hairline px-1 text-[10px] tracking-wide text-muted"
			>{badge}</span
		>
	{/if}
</span>
