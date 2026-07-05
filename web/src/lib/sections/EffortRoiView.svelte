<script lang="ts">
	import SectionHeader from '$lib/components/SectionHeader.svelte';
	import { effortRoi } from '$lib/benchmark';
	import { toolColor } from '$lib/tools';

	const sign = (x: number) => (x >= 0 ? '+' : '');
	const dRecallTone = (d: number) =>
		d > 0.005 ? 'var(--color-good)' : d < -0.005 ? 'var(--color-critical)' : 'var(--color-muted)';
</script>

{#if effortRoi.length}
	<section id="roi" class="mx-auto max-w-4xl px-6 py-16">
		<SectionHeader
			kicker="Effort ROI"
			title="What the next tier buys"
			dek="For each model with multiple effort tiers, the change at every step: how much recall you gain (in points), and what it costs in dollars and seconds."
		/>
		<div class="flex flex-col gap-8">
			{#each effortRoi as m (m.tool)}
				<div>
					<div class="mono mb-2 flex items-center gap-2 text-[13px] text-ink">
						<span class="inline-block h-2.5 w-2.5 rounded-[2px]" style="background: {toolColor(m.tool)}"></span>
						{m.modelLabel}
					</div>
					<div class="mono grid grid-cols-[1fr_5rem_5rem_5rem] gap-2 border-b border-dotted border-hairline pb-1 text-[11px] text-muted">
						<span>step</span><span class="text-right">Δ recall</span><span class="text-right">Δ $</span><span class="text-right">Δ speed</span>
					</div>
					{#each m.steps as s (s.from + s.to)}
						<div class="mono tabular grid grid-cols-[1fr_5rem_5rem_5rem] items-center gap-2 border-b border-hairline/40 py-1.5 text-[12px]">
							<span class="text-ink-2">{s.from} → {s.to}</span>
							<span class="text-right" style="color: {dRecallTone(s.dRecall)}">{sign(s.dRecall)}{Math.round(s.dRecall * 100)}%</span>
							<span class="text-right text-muted">{s.dCost != null ? `${sign(s.dCost)}$${Math.abs(s.dCost).toFixed(2)}` : '—'}</span>
							<span class="text-right text-muted">{s.dSpeed != null ? `${sign(s.dSpeed)}${s.dSpeed}s` : '—'}</span>
						</div>
					{/each}
				</div>
			{/each}
		</div>
		<p class="mono mt-4 text-[11px] text-muted">Δ recall in points · costs are per-run estimates · green = gain, red = loss</p>
	</section>
{/if}
