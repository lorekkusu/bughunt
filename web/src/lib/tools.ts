import type { ToolId, ToolKind, Severity } from './types';

/** CSS custom property carrying each model's fixed hue (never repainted by rank). */
export const toolColor = (id: ToolId): string => `var(--tool-${id})`;

export const kindBadge = (kind: ToolKind): string | null =>
	kind === 'native' ? 'native' : kind === 'manual' ? 'manual' : null;

export const SEVERITY_STATUS: Record<Severity, string> = {
	critical: 'var(--critical)',
	high: 'var(--serious)',
	medium: 'var(--warn)',
	low: 'var(--good)'
};

export const pct = (x: number): string => `${Math.round(x * 100)}%`;
