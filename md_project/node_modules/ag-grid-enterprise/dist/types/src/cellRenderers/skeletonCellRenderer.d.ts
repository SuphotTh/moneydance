import type { ILoadingCellRendererComp, ILoadingCellRendererParams } from 'ag-grid-community';
import { Component } from 'ag-grid-community';
export declare class SkeletonCellRenderer extends Component implements ILoadingCellRendererComp {
    constructor();
    init(params: ILoadingCellRendererParams): void;
    private setupFailed;
    private setupLoading;
    refresh(_params: ILoadingCellRendererParams): boolean;
}
