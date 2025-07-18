export interface RangeBarSeriesDataAggregationFilter {
    indexData: Int32Array;
    maxRange: number;
}
export declare function aggregateRangeBarData(xValues: any[], highValues: any[], lowValues: any[], domain: number[]): RangeBarSeriesDataAggregationFilter[] | undefined;
