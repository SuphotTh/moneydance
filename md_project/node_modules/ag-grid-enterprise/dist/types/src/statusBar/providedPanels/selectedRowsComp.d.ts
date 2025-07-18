import type { IStatusPanelComp } from 'ag-grid-community';
import { AgNameValue } from './agNameValue';
export declare class SelectedRowsComp extends AgNameValue implements IStatusPanelComp {
    postConstruct(): void;
    private onRowSelectionChanged;
    init(): void;
    refresh(): boolean;
}
