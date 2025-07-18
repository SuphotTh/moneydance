import type { IStatusPanelComp } from 'ag-grid-community';
import { AgNameValue } from './agNameValue';
export declare class FilteredRowsComp extends AgNameValue implements IStatusPanelComp {
    postConstruct(): void;
    private onDataChanged;
    private getTotalRowCountValue;
    private getFilteredRowCountValue;
    init(): void;
    refresh(): boolean;
}
