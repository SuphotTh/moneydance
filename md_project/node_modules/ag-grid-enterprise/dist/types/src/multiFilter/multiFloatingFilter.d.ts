import type { FilterChangedEvent, IFloatingFilterComp, IFloatingFilterParams, IMultiFilterModel } from 'ag-grid-community';
import { AgPromise, Component } from 'ag-grid-community';
import { MultiFilter } from './multiFilter';
export declare class MultiFloatingFilterComp extends Component implements IFloatingFilterComp<MultiFilter> {
    private floatingFilters;
    private compDetailsList;
    private params;
    constructor();
    init(params: IFloatingFilterParams<MultiFilter>): AgPromise<void>;
    private setParams;
    refresh(params: IFloatingFilterParams<MultiFilter>): void;
    private getCompDetailsList;
    onParentModelChanged(model: IMultiFilterModel, event: FilterChangedEvent): void;
    destroy(): void;
    private getCompDetails;
    private parentMultiFilterInstance;
}
