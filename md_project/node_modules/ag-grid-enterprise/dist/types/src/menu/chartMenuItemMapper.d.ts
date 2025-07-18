import type { MenuItemDef, NamedBean } from 'ag-grid-community';
import { BeanStub } from 'ag-grid-community';
export declare class ChartMenuItemMapper extends BeanStub implements NamedBean {
    beanName: "chartMenuItemMapper";
    getChartItems(key: 'pivotChart' | 'chartRange'): MenuItemDef | null;
    private cleanInternals;
    private buildLookup;
    /**
     * Make the MenuItem match the charts provided and their ordering on the ChartGroupsDef config object as provided by the user.
     */
    private filterAndOrderChartMenu;
}
export type PivotMenuOptionName = 'pivotChart' | 'pivotColumnChart' | 'pivotGroupedColumn' | 'pivotStackedColumn' | 'pivotNormalizedColumn' | 'pivotBarChart' | 'pivotGroupedBar' | 'pivotStackedBar' | 'pivotNormalizedBar' | 'pivotPieChart' | 'pivotPie' | 'pivotDonut' | 'pivotLineChart' | 'pivotStackedLine' | 'pivotNormalizedLine' | 'pivotXYChart' | 'pivotScatter' | 'pivotBubble' | 'pivotAreaChart' | 'pivotArea' | 'pivotStackedArea' | 'pivotNormalizedArea' | 'pivotStatisticalChart' | 'pivotHistogram' | 'pivotHierarchicalChart' | 'pivotTreemap' | 'pivotSunburst' | 'pivotCombinationChart' | 'pivotColumnLineCombo' | 'pivotAreaColumnCombo';
export type RangeMenuOptionName = 'chartRange' | 'rangeColumnChart' | 'rangeGroupedColumn' | 'rangeStackedColumn' | 'rangeNormalizedColumn' | 'rangeBarChart' | 'rangeGroupedBar' | 'rangeStackedBar' | 'rangeNormalizedBar' | 'rangePieChart' | 'rangePie' | 'rangeDonut' | 'rangeLineChart' | 'rangeStackedLine' | 'rangeNormalizedLine' | 'rangeXYChart' | 'rangeScatter' | 'rangeBubble' | 'rangeAreaChart' | 'rangeArea' | 'rangeStackedArea' | 'rangeNormalizedArea' | 'rangePolarChart' | 'rangeRadarLine' | 'rangeRadarArea' | 'rangeNightingale' | 'rangeRadialColumn' | 'rangeRadialBar' | 'rangeStatisticalChart' | 'rangeBoxPlot' | 'rangeHistogram' | 'rangeRangeBar' | 'rangeRangeArea' | 'rangeHierarchicalChart' | 'rangeTreemap' | 'rangeSunburst' | 'rangeSpecializedChart' | 'rangeWaterfall' | 'rangeHeatmap' | 'rangeCombinationChart' | 'rangeColumnLineCombo' | 'rangeAreaColumnCombo';
