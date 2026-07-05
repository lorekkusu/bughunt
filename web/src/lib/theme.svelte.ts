import { browser } from '$app/environment';

type Mode = 'light' | 'dark';

function initial(): Mode {
	if (!browser) return 'dark';
	const s = localStorage.getItem('theme');
	if (s === 'light' || s === 'dark') return s;
	return matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

class Theme {
	value = $state<Mode>(initial());

	#apply() {
		if (browser) document.documentElement.classList.toggle('dark', this.value === 'dark');
	}

	toggle() {
		this.value = this.value === 'dark' ? 'light' : 'dark';
		if (browser) {
			localStorage.setItem('theme', this.value);
			this.#apply();
		}
	}
}

export const theme = new Theme();
