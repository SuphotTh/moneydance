import type { ChartType } from 'ag-grid-community';
import type { AgChartsExports } from '../../../../../agChartsExports';
import { MiniChartWithAxes } from '../miniChartWithAxes';
export interface Coordinate {
    x: number;
    y: number;
}
export declare class MiniAreaColumnCombo extends MiniChartWithAxes {
    static chartType: ChartType;
    private columns;
    private areas;
    private columnData;
    private areaData;
    constructor(container: HTMLElement, agChartsExports: AgChartsExports, fills: string[], strokes: string[]);
    updateColors(fills: string[], strokes: string[]): void;
}
