export type Severity = 'critical' | 'high' | 'medium' | 'low';
/** Tool ids are config-driven (slug of the provider's `label`), so: string. */
export type ToolId = string;
export type ToolKind = 'model' | 'native' | 'manual';

export interface Tool {
	id: ToolId; // slug of the model — the series identity
	model: string; // raw model id
	modelLabel: string; // primary display, e.g. "opus-4.8"
	providerLabel: string; // secondary display, e.g. "claude"
	kind: ToolKind;
	color: { light: string; dark: string };
}

export interface Bug {
	id: string;
	severity: Severity;
	title: string;
	file: string;
	symbol: string;
}

export interface Project {
	id: string;
	label: string;
	theme: string;
	bugs: Bug[];
}

export interface Stat3 {
	mean: number;
	min: number;
	max: number;
}

export interface Config {
	tool: ToolId;
	provider: string;
	model: string;
	effort: string;
	project: string;
	promptId: string;
	native: boolean;
	manual: boolean;
	runs: number;
	recall: Stat3;
	fp: number;
	bonus: number;
	speedS: number | null;
	cost: number | null;
	perBug: Record<string, number>;
}

export interface SeverityCount {
	found: number;
	possible: number;
}

export interface Overall {
	tool: ToolId;
	provider: string;
	model: string;
	effort: string;
	native: boolean;
	manual: boolean;
	projects: number;
	recall: number;
	bySeverity: Record<Severity, SeverityCount>;
	fp: number;
	cost: number | null; // mean $/run
	costTotal: number | null; // sum across projects (one full pass)
	bonusTotal: number; // extra real bugs found, summed
	speedMean: number | null; // mean s/run
}

export interface Benchmark {
	meta: {
		generatedFrom: string;
		projects: number;
		tools: number;
		configs: number;
		totalPlanted: number;
		bugsPerProject: number | null; // the common count, or null if projects differ
		plantedBySeverity: Record<Severity, number>;
		runsDefault: number;
	};
	severities: Severity[];
	effortOrder: string[];
	tools: Tool[];
	projects: Project[];
	configs: Config[];
	overall: Overall[];
}
