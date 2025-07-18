export interface RangeAreaSeriesDataAggregationFilter {
    maxRange: number;
    topIndices: number[];
    bottomIndices: number[];
}
export declare function aggregateData(xValues: any[], highValues: any[], lowValues: any[], domain: number[]): RangeAreaSeriesDataAggregationFilter[] | undefined;
