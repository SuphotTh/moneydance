import type { NamedBean, RefreshModelParams } from 'ag-grid-community';
import { AbstractClientSideTreeNodeManager } from './abstractClientSideTreeNodeManager';
export declare class ClientSidePathTreeNodeManager<TData> extends AbstractClientSideTreeNodeManager<TData> implements NamedBean {
    beanName: "csrmPathTreeNodeSvc";
    protected loadNewRowData(rowData: TData[]): void;
    get treeData(): boolean;
    refreshModel(params: RefreshModelParams<TData>): void;
    private executeTransactions;
    private addOrUpdateRow;
}
