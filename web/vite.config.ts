import tailwindcss from '@tailwindcss/vite';
import adapter from '@sveltejs/adapter-static';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [
		tailwindcss(),
		sveltekit({
			compilerOptions: {
				// Force runes mode for the project, except for libraries. Can be removed in svelte 6.
				runes: ({ filename }) =>
					filename.split(/[/\\]/).includes('node_modules') ? undefined : true
			},

			// Static, fully-prerendered report site. BASE_PATH is set by CI for a
			// GitHub Pages project site (e.g. /bughunt); empty for local builds.
			adapter: adapter(),
			paths: { base: (process.env.BASE_PATH ?? '') as '' | `/${string}` }
		})
	]
});
