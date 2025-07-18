import type { ChartType } from 'ag-grid-community';
import type { AgChartsExports } from '../../../../../agChartsExports';
import type { ThemeTemplateParameters } from '../../miniChartsContainer';
import { MiniStackedBar } from './miniStackedBar';
export declare class MiniNormalizedBar extends MiniStackedBar {
    static chartType: ChartType;
    static data: number[][];
    constructor(container: HTMLElement, agChartsExports: AgChartsExports, fills: string[], strokes: string[], themeTemplateParameters: ThemeTemplateParameters, isCustomTheme: boolean);
}
