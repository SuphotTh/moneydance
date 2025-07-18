import type { ChartType } from 'ag-grid-community';
import type { AgChartsExports } from '../../../../../agChartsExports';
import { MiniChart } from '../miniChart';
export declare class MiniCustomCombo extends MiniChart {
    static chartType: ChartType;
    private columns;
    private lines;
    private columnData;
    private lineData;
    constructor(container: HTMLElement, agChartsExports: AgChartsExports, fills: string[], strokes: string[]);
    updateColors(fills: string[], strokes: string[]): void;
    buildPenIconPath(penIcon: any): void;
}
