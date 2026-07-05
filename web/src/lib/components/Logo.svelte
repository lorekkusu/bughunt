<script lang="ts">
	// The bughunt mark: a 3×3 lattice of dots with one anomaly — a red square,
	// tilted and nudged out of the grid (the bug that broke rank). Dots inherit
	// currentColor so the mark themes with its surroundings; the accent stays red.
	let { size = 20 }: { size?: number } = $props();
</script>

<svg width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden="true">
	<g fill="currentColor" opacity="0.32">
		<circle cx="5" cy="5" r="2.1" />
		<circle cx="12" cy="5" r="2.1" />
		<circle cx="5" cy="12" r="2.1" />
		<circle cx="12" cy="12" r="2.1" />
		<circle cx="19" cy="12" r="2.1" />
		<circle cx="5" cy="19" r="2.1" />
		<circle cx="12" cy="19" r="2.1" />
		<circle cx="19" cy="19" r="2.1" />
	</g>
	<rect x="17.8" y="1.2" width="5" height="5" rx="1.1" fill="#db4a3a" transform="rotate(15 20.3 3.7)" />
</svg>
