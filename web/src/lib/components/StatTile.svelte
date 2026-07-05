<script lang="ts">
	import { Tween } from 'svelte/motion';
	import { cubicOut } from 'svelte/easing';

	let {
		value,
		prefix = '',
		suffix = '',
		decimals = 0,
		label,
		note = '',
		tone = 'ink',
		animate = true
	}: {
		value: number;
		prefix?: string;
		suffix?: string;
		decimals?: number;
		label: string;
		note?: string;
		tone?: 'ink' | 'good' | 'critical';
		animate?: boolean;
	} = $props();

	const reduce =
		typeof matchMedia !== 'undefined' && matchMedia('(prefers-reduced-motion: reduce)').matches;
	const tween = new Tween(animate && !reduce ? 0 : value, { duration: 900, easing: cubicOut });

	let el: HTMLElement;
	$effect(() => {
		if (!animate || reduce) return;
		const io = new IntersectionObserver(
			(entries) => {
				if (entries[0].isIntersecting) {
					tween.set(value);
					io.disconnect();
				}
			},
			{ threshold: 0.4 }
		);
		if (el) io.observe(el);
		return () => io.disconnect();
	});

	const toneVar: Record<string, string> = {
		ink: 'var(--color-ink)',
		good: 'var(--color-good)',
		critical: 'var(--color-critical)'
	};
</script>

<div bind:this={el} class="flex flex-col gap-1">
	<div class="mono tabular text-[clamp(2rem,5vw,2.75rem)] leading-none" style="color: {toneVar[tone]}">
		{prefix}{tween.current.toFixed(decimals)}{suffix}
	</div>
	<div class="mono text-[12px] tracking-wide text-ink-2 uppercase">{label}</div>
	{#if note}
		<div class="text-[13px] text-muted">{note}</div>
	{/if}
</div>
