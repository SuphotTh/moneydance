import type { ITreeNode, RowNode } from 'ag-grid-community';
/**
 * This is the type of any row processed by the TreeStrategy.
 *
 * TreeStrategy can modify:
 * - allLeafChildren
 * - childrenAfterGroup
 * - treeNode
 * - treeNodeFlags
 */
export interface TreeRow<TData = any> extends RowNode<TData> {
    allLeafChildren: TreeRow<TData>[] | null;
    childrenAfterGroup: TreeRow<TData>[] | null;
    treeNode: ITreeNode | null;
    treeNodeFlags: number;
    sibling: TreeRow<TData>;
    sourceRowIndex: number;
}
/** We set this on the first time the node is committed. We unset this if the row gets deleted. */
export declare const isTreeRowCommitted: (row: RowNode) => boolean;
/** Check if the expanded state needs to be initialized, first time for a node, or again if the node was removed */
export declare const isTreeRowExpandedInitialized: (row: RowNode) => boolean;
/** We use this to mark a row as updated by an updated transaction */
export declare const isTreeRowUpdated: (row: RowNode) => boolean;
/** We use this to see if a row changed key during commit */
export declare const isTreeRowKeyChanged: (row: RowNode) => boolean;
/** Returns true if markTreeRowPathChanged was called. Reset during commit.  */
export declare const isTreeRowPathChanged: (row: TreeRow) => boolean;
/** Changes the expanded initialized state, so it can be recomputed again. */
export declare const setTreeRowExpandedInitialized: (row: TreeRow, value: boolean) => void;
/**
 * We use this to mark a row as updated by an updated transaction.
 * This will be set only if the row was committed at least once before.
 */
export declare const setTreeRowUpdated: (row: TreeRow) => void;
/**
 * We use this to mark that a row changed key during commit.
 * This will be set only if the row was committed at least once before.
 */
export declare const setTreeRowKeyChanged: (row: TreeRow) => void;
/** If this is true, commit stage must invoke changedPath.addParentNode */
export declare const markTreeRowPathChanged: (row: TreeRow) => void;
/** Called when the row is committed. */
export declare const markTreeRowCommitted: (row: TreeRow) => void;
/** Clears all the flags, called when the row is deleted from the tree */
export declare const clearTreeRowFlags: (row: TreeRow) => void;
