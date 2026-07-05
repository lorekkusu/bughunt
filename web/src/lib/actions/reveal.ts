import type { Action } from 'svelte/action';

/** Adds `.in` when the element first scrolls into view (once). Pair with `.reveal`. */
export const reveal: Action<HTMLElement, { threshold?: number; delay?: number } | undefined> = (
	node,
	opts
) => {
	const threshold = opts?.threshold ?? 0.15;
	const delay = opts?.delay ?? 0;
	if (delay) node.style.transitionDelay = `${delay}ms`;

	const io = new IntersectionObserver(
		(entries) => {
			for (const e of entries) {
				if (e.isIntersecting) {
					node.classList.add('in');
					io.unobserve(node);
				}
			}
		},
		{ threshold }
	);
	io.observe(node);
	return { destroy: () => io.disconnect() };
};
