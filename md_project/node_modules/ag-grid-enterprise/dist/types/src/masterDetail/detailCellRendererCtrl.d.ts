import type { GridApi, IDetailCellRenderer, IDetailCellRendererCtrl, IDetailCellRendererParams } from 'ag-grid-community';
import { BeanStub } from 'ag-grid-community';
export declare class DetailCellRendererCtrl extends BeanStub implements IDetailCellRendererCtrl {
    private params;
    private comp;
    private loadRowDataVersion;
    private refreshStrategy;
    init(comp: IDetailCellRenderer, params: IDetailCellRendererParams): void;
    private onFullWidthRowFocused;
    private setAutoHeightClasses;
    private setupRefreshStrategy;
    private createDetailGrid;
    registerDetailWithMaster(api: GridApi): void;
    private loadRowData;
    refresh(): boolean;
}
