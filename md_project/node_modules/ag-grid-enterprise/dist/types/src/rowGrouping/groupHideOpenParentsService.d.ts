import type { ChangedPath, Column, IGroupHideOpenParentsService, IRowNode, RowNode } from 'ag-grid-community';
import { BeanStub } from 'ag-grid-community';
export declare class GroupHideOpenParentsService extends BeanStub implements IGroupHideOpenParentsService {
    beanName: "groupHideOpenParentsSvc";
    updateGroupDataForHideOpenParents(changedPath?: ChangedPath): void;
    pullDownGroupDataForHideOpenParents(rowNodes: RowNode[] | null, clearOperation: boolean): void;
    isShowingValueForOpenedParent(rowNode: IRowNode, column: Column): boolean;
    private getFirstChildOfFirstChild;
}
