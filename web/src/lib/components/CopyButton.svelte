<script lang="ts">
	import copyMarkdown from '$lib/generated/copy.md?raw';

	let state = $state<'idle' | 'copied' | 'error'>('idle');
	let timer: ReturnType<typeof setTimeout>;

	async function copy() {
		try {
			await navigator.clipboard.writeText(copyMarkdown);
			state = 'copied';
		} catch {
			state = 'error';
		}
		clearTimeout(timer);
		timer = setTimeout(() => (state = 'idle'), 1800);
	}
</script>

<button
	type="button"
	onclick={copy}
	class="mono flex items-center gap-1.5 rounded-sm border border-hairline px-2 py-1 text-[12px] text-ink-2 transition-colors hover:text-ink"
	title="Copy a Markdown snapshot of the data + interpretation — paste it into your AI to discuss which tool fits you"
	aria-label="Copy the benchmark as Markdown for an AI assistant"
>
	<span aria-hidden="true">{state === 'copied' ? '✓' : state === 'error' ? '⚠' : '⧉'}</span>
	<span>{state === 'copied' ? 'copied' : state === 'error' ? 'failed' : 'copy for AI'}</span>
</button>
