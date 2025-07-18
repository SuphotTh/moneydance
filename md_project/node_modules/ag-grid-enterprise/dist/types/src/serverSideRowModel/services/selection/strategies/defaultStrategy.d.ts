import type { BeanCollection, IServerSideGroupSelectionState, IServerSideSelectionState, ISetNodesSelectedParams, RowNode } from 'ag-grid-community';
import { BeanStub } from 'ag-grid-community';
import type { ISelectionStrategy } from './iSelectionStrategy';
export declare class DefaultStrategy extends BeanStub implements ISelectionStrategy {
    private rowModel;
    private selectionSvc?;
    wireBeans(beans: BeanCollection): void;
    private selectedState;
    private selectAllUsed;
    private selectedNodes;
    getSelectedState(): IServerSideSelectionState;
    setSelectedState(state: IServerSideSelectionState | IServerSideGroupSelectionState): void;
    deleteSelectionStateFromParent(parentPath: string[], removedNodeIds: string[]): boolean;
    setNodesSelected(params: ISetNodesSelectedParams): number;
    processNewRow(node: RowNode<any>): void;
    isNodeSelected(node: RowNode): boolean | undefined;
    getSelectedNodes(): RowNode<any>[];
    getSelectedRows(): any[];
    getSelectionCount(): number;
    isEmpty(): boolean;
    selectAllRowNodes(): void;
    deselectAllRowNodes(): void;
    getSelectAllState(): boolean | null;
}
