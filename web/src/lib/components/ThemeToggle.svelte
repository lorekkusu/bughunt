<script lang="ts">
	import { theme } from '$lib/theme.svelte';
</script>

<button
	type="button"
	onclick={() => theme.toggle()}
	class="mono flex items-center gap-1.5 rounded-sm border border-hairline px-2 py-1 text-[12px] text-ink-2 transition-colors hover:text-ink"
	aria-label="Toggle color theme"
>
	<span aria-hidden="true">{theme.value === 'dark' ? '◑' : '◐'}</span>
	<span>{theme.value === 'dark' ? 'dark' : 'light'}</span>
</button>
