<script lang="ts">
	import './layout.css';
	import { base } from '$app/paths';
	import ThemeToggle from '$lib/components/ThemeToggle.svelte';
	import CopyButton from '$lib/components/CopyButton.svelte';
	import Logo from '$lib/components/Logo.svelte';

	let { children } = $props();

	const nav = [
		{ href: '#overall', label: 'overall' },
		{ href: '#perbug', label: 'per-bug' },
		{ href: '#hardest', label: 'difficulty' },
		{ href: '#ensemble', label: 'ensemble' },
		{ href: '#effort', label: 'effort' },
		{ href: '#cost', label: 'cost' },
		{ href: '#results', label: 'results' }
	];
</script>

<div class="min-h-screen">
	<header
		class="sticky top-0 z-20 border-b border-hairline bg-plane/80 backdrop-blur-md"
	>
		<div class="mx-auto flex max-w-4xl items-center justify-between px-6 py-3">
			<a href={base || '/'} class="mono flex items-center gap-2 text-[14px] font-medium text-ink">
				<Logo size={20} />
				bughunt
			</a>
			<nav class="flex items-center gap-5">
				{#each nav as n (n.href)}
					<a href={n.href} class="mono hidden text-[12px] text-ink-2 transition-colors hover:text-ink sm:inline">
						{n.label}
					</a>
				{/each}
				<CopyButton />
				<ThemeToggle />
			</nav>
		</div>
	</header>

	<main>
		{@render children()}
	</main>

	<footer class="mt-24 border-t border-hairline">
		<div class="mx-auto flex max-w-4xl flex-col gap-2 px-6 py-10 text-[13px] text-muted sm:flex-row sm:items-center sm:justify-between">
			<p>
				An informal, honest benchmark. Data generated from
				<span class="mono">harness/results</span>.
			</p>
			<a
				href="https://github.com/lorekkusu/bughunt"
				class="mono text-ink-2 transition-colors hover:text-ink">github.com/lorekkusu/bughunt</a
			>
		</div>
	</footer>
</div>
