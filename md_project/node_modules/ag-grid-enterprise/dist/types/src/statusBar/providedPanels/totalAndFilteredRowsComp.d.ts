import type { IStatusPanelComp } from 'ag-grid-community';
import { AgNameValue } from './agNameValue';
export declare class TotalAndFilteredRowsComp extends AgNameValue implements IStatusPanelComp {
    postConstruct(): void;
    private onDataChanged;
    private getFilteredRowCountValue;
    private getTotalRowCount;
    init(): void;
    refresh(): boolean;
}
