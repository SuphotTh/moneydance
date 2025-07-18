import { SPAN } from '../../utils/aggregation';
export declare const OPEN = 0;
export declare const HIGH = 3;
export declare const LOW = 2;
export declare const CLOSE = 1;
export { SPAN };
export interface OhlcSeriesDataAggregationFilter {
    indexData: Int32Array;
    maxRange: number;
}
export declare function aggregateOhlcData(xValues: any[], highValues: any[], lowValues: any[], domain: number[]): OhlcSeriesDataAggregationFilter[] | undefined;
