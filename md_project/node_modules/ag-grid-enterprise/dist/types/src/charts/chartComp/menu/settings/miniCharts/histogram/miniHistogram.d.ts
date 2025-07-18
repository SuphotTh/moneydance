import type { ChartType } from 'ag-grid-community';
import type { AgChartsExports } from '../../../../../agChartsExports';
import { MiniChartWithAxes } from '../miniChartWithAxes';
export declare class MiniHistogram extends MiniChartWithAxes {
    static chartType: ChartType;
    private readonly bars;
    constructor(container: HTMLElement, agChartsExports: AgChartsExports, fills: string[], strokes: string[]);
    updateColors([fill]: string[], [stroke]: string[]): void;
}
