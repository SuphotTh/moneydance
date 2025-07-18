import type { BeanCollection, IServerSideGroupSelectionState, IServerSideSelectionState, ISetNodesSelectedParams, RowNode } from 'ag-grid-community';
import { BeanStub } from 'ag-grid-community';
import type { ISelectionStrategy } from './iSelectionStrategy';
export declare class GroupSelectsChildrenStrategy extends BeanStub implements ISelectionStrategy {
    private rowModel;
    private rowGroupColsSvc?;
    private filterManager?;
    private selectionSvc;
    wireBeans(beans: BeanCollection): void;
    private selectedState;
    postConstruct(): void;
    getSelectedState(): IServerSideGroupSelectionState;
    setSelectedState(state: IServerSideSelectionState | IServerSideGroupSelectionState): void;
    deleteSelectionStateFromParent(parentRoute: string[], removedNodeIds: string[]): boolean;
    setNodesSelected({ nodes, newValue, clearSelection }: ISetNodesSelectedParams): number;
    isNodeSelected(node: RowNode): boolean | undefined;
    private isNodePathSelected;
    private getRouteToNode;
    private removeRedundantState;
    private recursivelySelectNode;
    getSelectedNodes(): RowNode<any>[];
    processNewRow(): void;
    getSelectedRows(): any[];
    getSelectionCount(): number;
    isEmpty(): boolean;
    selectAllRowNodes(): void;
    deselectAllRowNodes(): void;
    getSelectAllState(): boolean | null;
}
