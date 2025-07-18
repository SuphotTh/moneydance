import type { ChartType } from 'ag-grid-community';
import type { AgChartsExports } from '../../../../../agChartsExports';
import { MiniChartWithAxes } from '../miniChartWithAxes';
export declare class MiniColumnLineCombo extends MiniChartWithAxes {
    static chartType: ChartType;
    private columns;
    private lines;
    private columnData;
    private lineData;
    constructor(container: HTMLElement, agChartsExports: AgChartsExports, fills: string[], strokes: string[]);
    updateColors(fills: string[], strokes: string[]): void;
}
