import type { ChartType } from 'ag-grid-community';
import type { AgChartsExports } from '../../../../../agChartsExports';
import type { ChartTranslationKey } from '../../../../services/chartTranslationService';
import type { ThemeTemplateParameters } from '../../miniChartsContainer';
import { MiniStackedArea } from './miniStackedArea';
export declare class MiniNormalizedArea extends MiniStackedArea {
    static chartType: ChartType;
    static readonly data: number[][];
    constructor(container: HTMLElement, agChartsExports: AgChartsExports, fills: string[], strokes: string[], themeTemplateParameters: ThemeTemplateParameters, isCustomTheme: boolean, data?: number[][], tooltipName?: ChartTranslationKey);
}
