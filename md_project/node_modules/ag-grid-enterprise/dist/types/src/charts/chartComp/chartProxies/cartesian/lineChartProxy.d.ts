import type { AgCartesianAxisOptions, AgLineSeriesOptions } from 'ag-charts-types';
import type { ChartProxyParams, UpdateParams } from '../chartProxy';
import { CartesianChartProxy } from './cartesianChartProxy';
export declare class LineChartProxy extends CartesianChartProxy<'line'> {
    constructor(params: ChartProxyParams);
    protected getAxes(params: UpdateParams): AgCartesianAxisOptions[];
    protected getSeries(params: UpdateParams): (AgLineSeriesOptions<any> | import("ag-charts-types").AgAreaSeriesOptions<any>)[];
    private isNormalised;
}
