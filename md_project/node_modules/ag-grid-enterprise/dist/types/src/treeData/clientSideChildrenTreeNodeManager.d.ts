import type { IClientSideNodeManager, NamedBean, RefreshModelParams, RowNode } from 'ag-grid-community';
import { AbstractClientSideTreeNodeManager } from './abstractClientSideTreeNodeManager';
export declare class ClientSideChildrenTreeNodeManager<TData> extends AbstractClientSideTreeNodeManager<TData> implements IClientSideNodeManager<TData>, NamedBean {
    beanName: "csrmChildrenTreeNodeSvc";
    private childrenGetter;
    get treeData(): boolean;
    extractRowData(): TData[] | null | undefined;
    destroy(): void;
    activate(rootNode: RowNode<TData>): void;
    protected loadNewRowData(rowData: TData[]): void;
    setImmutableRowData(params: RefreshModelParams<TData>, rowData: TData[]): void;
    refreshModel(params: RefreshModelParams<TData>): void;
}
