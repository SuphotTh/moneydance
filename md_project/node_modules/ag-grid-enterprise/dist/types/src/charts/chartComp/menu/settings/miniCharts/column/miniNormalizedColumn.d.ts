import type { ChartType } from 'ag-grid-community';
import type { AgChartsExports } from '../../../../../agChartsExports';
import type { ThemeTemplateParameters } from '../../miniChartsContainer';
import { MiniStackedColumn } from './miniStackedColumn';
export declare class MiniNormalizedColumn extends MiniStackedColumn {
    static chartType: ChartType;
    static data: number[][];
    constructor(container: HTMLElement, agChartsExports: AgChartsExports, fills: string[], strokes: string[], themeTemplateParameters: ThemeTemplateParameters, isCustomTheme: boolean);
}
