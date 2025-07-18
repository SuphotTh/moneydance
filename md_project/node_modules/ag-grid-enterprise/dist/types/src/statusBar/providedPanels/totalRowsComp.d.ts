import type { IStatusPanelComp } from 'ag-grid-community';
import { AgNameValue } from './agNameValue';
export declare class TotalRowsComp extends AgNameValue implements IStatusPanelComp {
    postConstruct(): void;
    private onDataChanged;
    private getRowCountValue;
    init(): void;
    refresh(): boolean;
}
