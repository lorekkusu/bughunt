<script lang="ts">
	let {
		kicker,
		title,
		dek = ''
	}: { kicker: string; title: string; dek?: string } = $props();
</script>

<header class="mb-8 flex flex-col gap-3">
	<div class="mono text-[12px] tracking-[0.15em] text-muted uppercase">{kicker}</div>
	<h2 class="max-w-3xl text-[clamp(1.5rem,3.5vw,2.25rem)] leading-tight font-semibold tracking-tight">
		{title}
	</h2>
	{#if dek}
		<p class="max-w-2xl text-[15px] text-ink-2">{dek}</p>
	{/if}
</header>
