import type { ChartType } from 'ag-grid-community';
import type { AgChartsExports } from '../../../../../agChartsExports';
import type { ThemeTemplateParameters } from '../../miniChartsContainer';
import { MiniDonut } from './miniDonut';
export declare class MiniPie extends MiniDonut {
    static chartType: ChartType;
    constructor(container: HTMLElement, agChartsExports: AgChartsExports, fills: string[], strokes: string[], themeTemplateParameters: ThemeTemplateParameters, isCustomTheme: boolean);
}
