<script lang="ts">
	import Hero from '$lib/sections/Hero.svelte';
	import MethodStrip from '$lib/sections/MethodStrip.svelte';
	import Overview from '$lib/sections/Overview.svelte';
	import PerBugView from '$lib/sections/PerBugView.svelte';
	import HardestBugs from '$lib/sections/HardestBugs.svelte';
	import EnsembleView from '$lib/sections/EnsembleView.svelte';
	import EffortView from '$lib/sections/EffortView.svelte';
	import EffortRoiView from '$lib/sections/EffortRoiView.svelte';
	import ValueView from '$lib/sections/ValueView.svelte';
	import EfficiencyView from '$lib/sections/EfficiencyView.svelte';
	import PrecisionView from '$lib/sections/PrecisionView.svelte';
	import Interpretation from '$lib/sections/Interpretation.svelte';
	import Closing from '$lib/sections/Closing.svelte';
</script>

<svelte:head>
	<title>bughunt — an honest AI code-review benchmark</title>
</svelte:head>

<Hero />
<div id="method"></div>
<MethodStrip />
<Overview />
<PerBugView />
<HardestBugs />
<EnsembleView />
<EffortView />
<EffortRoiView />
<ValueView />
<EfficiencyView />
<PrecisionView />
<Interpretation />
<Closing />
