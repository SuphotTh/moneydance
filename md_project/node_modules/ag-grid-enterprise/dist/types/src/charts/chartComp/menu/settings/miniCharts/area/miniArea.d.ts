import type { Path } from 'ag-charts-types/scene';
import type { ChartType } from 'ag-grid-community';
import type { AgChartsExports } from '../../../../../agChartsExports';
import type { ChartTranslationKey } from '../../../../services/chartTranslationService';
import type { ThemeTemplateParameters } from '../../miniChartsContainer';
import { MiniChartWithAxes } from '../miniChartWithAxes';
export declare class MiniArea extends MiniChartWithAxes {
    static chartType: ChartType;
    protected readonly areas: Path[];
    static readonly data: number[][];
    constructor(container: HTMLElement, agChartsExports: AgChartsExports, fills: string[], strokes: string[], _themeTemplateParameters: ThemeTemplateParameters, _isCustomTheme: boolean, data?: number[][], tooltipName?: ChartTranslationKey, stacked?: boolean);
    updateColors(fills: string[], strokes: string[]): void;
}
