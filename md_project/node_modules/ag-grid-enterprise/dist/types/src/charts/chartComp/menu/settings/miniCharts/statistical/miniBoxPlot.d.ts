import type { ChartType } from 'ag-grid-community';
import type { AgChartsExports } from '../../../../../agChartsExports';
import type { ThemeTemplateParameters } from '../../miniChartsContainer';
import { MiniChartWithAxes } from '../miniChartWithAxes';
export declare class MiniBoxPlot extends MiniChartWithAxes {
    static chartType: ChartType;
    private readonly boxPlotGroups;
    constructor(container: HTMLElement, agChartsExports: AgChartsExports, fills: string[], strokes: string[], themeTemplateParameters: ThemeTemplateParameters, isCustomTheme: boolean);
    updateColors(fills: string[], strokes: string[], themeTemplateParameters?: ThemeTemplateParameters, isCustomTheme?: boolean): void;
    setLineProperties(line: any, x1: number, x2: number, y1: number, y2: number): void;
}
