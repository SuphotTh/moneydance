import { _ModuleSupport } from 'ag-charts-community';
import { type OhlcNodeDatum, OhlcSeriesBase } from '../ohlc/ohlcSeriesBase';
import { CandlestickNode } from './candlestickNode';
import { CandlestickSeriesProperties } from './candlestickSeriesProperties';
export declare class CandlestickSeries extends OhlcSeriesBase<CandlestickNode, CandlestickSeriesProperties<any>> {
    static readonly className = "CandleStickSeries";
    static readonly type: "candlestick";
    properties: CandlestickSeriesProperties<import("ag-charts-community").AgOhlcSeriesBaseOptions>;
    protected nodeFactory(): CandlestickNode;
    protected updateDatumNodes({ datumSelection, isHighlight, }: {
        datumSelection: _ModuleSupport.Selection<CandlestickNode, OhlcNodeDatum>;
        isHighlight: boolean;
    }): void;
    private legendItemSymbol;
    getLegendData(legendType: _ModuleSupport.ChartLegendType): _ModuleSupport.CategoryLegendDatum[];
}
