import type { IToolPanelComp, IToolPanelParams, ToolPanelDef, WithoutGridCommon } from 'ag-grid-community';
import { Component } from 'ag-grid-community';
export declare class ToolPanelWrapper extends Component {
    private toolPanelCompInstance;
    private toolPanelId;
    private resizeBar;
    private width;
    private params;
    constructor();
    postConstruct(): void;
    getToolPanelId(): string;
    setToolPanelDef(toolPanelDef: ToolPanelDef, params: WithoutGridCommon<IToolPanelParams>): boolean;
    private setToolPanelComponent;
    getToolPanelInstance(): IToolPanelComp | undefined;
    setResizerSizerSide(side: 'right' | 'left'): void;
    refresh(): void;
}
