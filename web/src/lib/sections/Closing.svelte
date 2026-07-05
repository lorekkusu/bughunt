<script lang="ts">
	import { reveal } from '$lib/actions/reveal';
</script>

<section id="why" class="border-t border-hairline">
	<div class="mx-auto max-w-4xl px-6 py-20">
		<div class="mono mb-6 text-[12px] tracking-[0.15em] text-muted uppercase">Why this exists</div>
		<div class="flex max-w-2xl flex-col gap-5 text-[16px] leading-relaxed text-ink-2" use:reveal>
			<p>
				I care about code review. As AI writes more of the code — and writes it faster — picking the
				right reviewer has quietly become the thing I spend the most effort on, and the thing I could
				find the least honest data about. Almost every tool claims higher recall and less noise than
				the rest; almost none of them show the numbers.
			</p>
			<p>
				This isn't a formal or authoritative benchmark, and it may not discriminate as sharply as I'd
				like. But even a small, open experiment starts to surface the questions that actually matter:
				does more reasoning effort really help? Do the purpose-built reviewers earn their price? —
				especially as that price climbs: free tiers are tightening, and hosted reviews are creeping
				toward a dollar a pull request. When review gets expensive, running your own in CI (something
				like <span class="mono text-ink">pr-agent</span>, or a small harness of your own) becomes a
				real way to keep costs down — which turns
				<span class="text-ink">“which model, at what effort, for how much time and money?”</span> into
				a question worth measuring.
			</p>
			<p>
				I don't expect this to be the last word. I just hope it's a useful reference for anyone
				wrestling with the same choice — read the results here, or
				<a
					href="https://github.com/lorekkusu/bughunt"
					class="text-ink underline decoration-hairline underline-offset-4 transition-colors hover:decoration-ink-2"
					>fork it</a
				>, add your own projects, and run it yourself.
			</p>
			<p class="mono mt-2 text-[12px] text-muted">an informal, open experiment · MIT-licensed</p>
		</div>
	</div>
</section>
