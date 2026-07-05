<script lang="ts">
	import { meta } from '$lib/benchmark';

	const defs = [
		{ term: 'recall', body: "share of a project's planted bugs a tool found. The headline metric." },
		{ term: 'FP', body: 'false positives per run — real code wrongly flagged. The second axis.' },
		{ term: 'bonus', body: 'extra real issues found beyond the planted set (not scored as recall).' },
		{ term: 'native', body: "the tool ran its own review engine, not our shared prompt — so it's not directly comparable." }
	];
	const stability = [
		{ g: '✅', t: 'every run', c: 'var(--color-seq-every)' },
		{ g: '⚠️', t: 'some runs', c: 'var(--color-seq-some)' },
		{ g: '❌', t: 'never', c: 'var(--color-muted)' }
	];
</script>

<section class="mx-auto max-w-4xl px-6 py-12">
	<div class="grid gap-8 rounded-md border border-hairline bg-surface/40 p-6 sm:grid-cols-[1.4fr_1fr] sm:gap-10">
		<div class="flex flex-col gap-5">
			<div class="mono text-[12px] tracking-[0.15em] text-muted uppercase">How to read this</div>
			<div class="flex flex-wrap gap-x-6 gap-y-2">
				{#each stability as s (s.t)}
					<span class="flex items-center gap-2 text-[13px] text-ink-2">
						<span aria-hidden="true">{s.g}</span>
						<span class="mono" style="color: {s.c}">{s.t}</span>
					</span>
				{/each}
				<span class="text-[13px] text-muted">— per-bug stability across {meta.runsDefault} runs</span>
			</div>
			<dl class="grid gap-x-6 gap-y-2 sm:grid-cols-2">
				{#each defs as d (d.term)}
					<div class="text-[13px] leading-snug">
						<dt class="mono inline text-ink">{d.term}</dt>
						<dd class="inline text-ink-2"> — {d.body}</dd>
					</div>
				{/each}
			</dl>
		</div>

		<div class="flex flex-col gap-2 border-t border-dotted border-hairline pt-5 sm:border-t-0 sm:border-l sm:pt-0 sm:pl-8">
			<div class="mono text-[12px] tracking-[0.15em] text-muted uppercase">Caveats</div>
			<p class="text-[13px] leading-relaxed text-ink-2">
				Small, fully-readable projects. A single LLM judge. One language (Python) so far. Costs are
				<span class="mono">API-equivalent list-price estimates</span>, not billed spend. This is an
				informal, one-person experiment — a directional signal, not gospel.
			</p>
		</div>
	</div>
</section>
