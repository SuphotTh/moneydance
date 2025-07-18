import type { ChartType } from 'ag-grid-community';
import type { AgChartsExports } from '../../../../../agChartsExports';
import type { ChartTranslationKey } from '../../../../services/chartTranslationService';
import type { ThemeTemplateParameters } from '../../miniChartsContainer';
import { MiniArea } from './miniArea';
export declare class MiniStackedArea extends MiniArea {
    static chartType: ChartType;
    static readonly data: number[][];
    constructor(container: HTMLElement, agChartsExports: AgChartsExports, fills: string[], strokes: string[], _themeTemplateParameters: ThemeTemplateParameters, _isCustomTheme: boolean, data?: number[][], tooltipName?: ChartTranslationKey);
    updateColors(fills: string[], strokes: string[]): void;
}
