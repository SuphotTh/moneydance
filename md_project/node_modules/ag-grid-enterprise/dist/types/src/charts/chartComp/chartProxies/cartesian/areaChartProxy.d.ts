import type { AgAreaSeriesOptions, AgCartesianAxisOptions } from 'ag-charts-types';
import type { ChartProxyParams, UpdateParams } from '../chartProxy';
import { CartesianChartProxy } from './cartesianChartProxy';
export declare class AreaChartProxy extends CartesianChartProxy<'area'> {
    constructor(params: ChartProxyParams);
    protected getAxes(params: UpdateParams): AgCartesianAxisOptions[];
    protected getSeries(params: UpdateParams): (import("ag-charts-types").AgLineSeriesOptions<any> | AgAreaSeriesOptions<any>)[];
    private isNormalised;
}
