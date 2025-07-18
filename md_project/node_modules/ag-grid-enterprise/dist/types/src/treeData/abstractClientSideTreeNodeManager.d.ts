import type { ChangedPath, InitialGroupOrderComparatorParams, IsGroupOpenByDefaultParams, RefreshModelParams, WithoutGridCommon } from 'ag-grid-community';
import { AbstractClientSideNodeManager, RowNode } from 'ag-grid-community';
import { TreeNode } from './treeNode';
export type IsGroupOpenByDefaultCallback = ((params: WithoutGridCommon<IsGroupOpenByDefaultParams>) => boolean) | undefined;
export type InitialGroupOrderComparatorCallback = ((params: WithoutGridCommon<InitialGroupOrderComparatorParams>) => number) | undefined;
export declare abstract class AbstractClientSideTreeNodeManager<TData> extends AbstractClientSideNodeManager<TData> {
    private oldGroupDisplayColIds;
    /** Rows that are pending deletion, this.commitDeletedRows() will finalize removal. */
    private rowsPendingDestruction;
    /** The root node of the tree. */
    treeRoot: TreeNode | null;
    activate(rootNode: RowNode<TData>): void;
    destroy(): void;
    deactivate(): void;
    /** Add or updates the row to a non-root node, preparing the tree correctly for the commit. */
    protected treeSetRow(node: TreeNode, newRow: RowNode, created: boolean): boolean;
    /**
     * Overwrites the row property of a non-root node to null.
     * @returns The previous row, if any, that was overwritten.
     */
    protected treeRemove(node: TreeNode, oldRow: RowNode): void;
    /** Commit the changes performed to the tree */
    protected treeCommit(changedPath?: ChangedPath): void;
    /** Calls commitChild for each invalidated child, recursively. We commit only the invalidated paths. */
    private treeCommitChildren;
    /** Commit the changes performed to a node and its children */
    private treeCommitChild;
    private treeCommitPreOrder;
    private treeCommitPostOrder;
    private createFillerRow;
    private setGroupData;
    /** Called to clear a subtree. */
    treeClear(node: TreeNode): void;
    /** Called by the deactivate, to destroy the whole tree. */
    private treeDestroy;
    /**
     * Finalizes the deletion of a row.
     * @param immediate If true, the row is deleted immediately.
     * If false, the row is marked for deletion, and will be deleted later with this.deleteDeletedRows()
     */
    private destroyRow;
    /**
     * destroyRow can defer the deletion to the end of the commit stage.
     * This method finalizes the deletion of rows that were marked for deletion.
     */
    private commitDestroyedRows;
    refreshModel(params: RefreshModelParams<TData>): void;
}
