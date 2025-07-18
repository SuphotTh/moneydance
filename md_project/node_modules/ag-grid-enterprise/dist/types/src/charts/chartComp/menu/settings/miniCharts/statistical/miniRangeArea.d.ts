import type { ChartType } from 'ag-grid-community';
import type { AgChartsExports } from '../../../../../agChartsExports';
import { MiniChartWithAxes } from '../miniChartWithAxes';
export declare class MiniRangeArea extends MiniChartWithAxes {
    static chartType: ChartType;
    private readonly lines;
    private readonly areas;
    constructor(container: HTMLElement, agChartsExports: AgChartsExports, fills: string[], strokes: string[]);
    updateColors(fills: string[], strokes: string[]): void;
    createRangeArea(root: any, data: Array<Array<{
        x: number;
        low: number;
        high: number;
    }>>, size: number, padding: number): {
        lines: any[][];
        areas: any[];
    };
}
