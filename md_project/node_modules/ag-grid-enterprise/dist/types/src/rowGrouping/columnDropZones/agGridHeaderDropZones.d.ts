import type { ComponentSelector } from 'ag-grid-community';
import { Component } from 'ag-grid-community';
export declare class AgGridHeaderDropZones extends Component {
    private rowGroupComp;
    private pivotComp;
    constructor();
    postConstruct(): void;
    private createNorthPanel;
    private onDropPanelVisible;
    private onRowGroupChanged;
    private onPivotPanelShow;
}
export declare const AgGridHeaderDropZonesSelector: ComponentSelector;
