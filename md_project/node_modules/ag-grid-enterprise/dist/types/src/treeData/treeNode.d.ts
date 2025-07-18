import type { ITreeNode } from 'ag-grid-community';
import type { TreeRow } from './treeRow';
/**
 * We keep a secondary tree data structure based on TreeNode together with the RowNodes.
 * We associate a RowNode with a TreeNode, both storing the row in node.row and by storing the TreeNode in row.treeNode field.
 * We break the association when the row is removed or the TreeStrategy destroyed.
 * Consider that a TreeNode can contain more than one RowNode if there are duplicates keys in the same group,
 * in this case it means that the rows will have the same TreeNode.
 *
 * TreeStrategy uses a two stage approach both for first time creation and updates.
 * Multiple updates interact with the tree, and a commit stage commits all updates reducing expensive computations.
 *
 * Operations that do not affect the order will invalidate only the affected paths with node.invalidate(),
 * so that the commit operation will only update the affected paths without traversing the whole tree.
 * Consider that order of invalidated items is not deterministic, so the commit operation should be able to handle any order.
 *
 * During commit, the childrenAfterGroup and allLeafChildren arrays are rebuilt, and the updates are applied.
 * The empty filler nodes nodes are removed.
 * Before commit those arrays are NOT representing the truth, so they should not be used.
 */
export declare class TreeNode implements ITreeNode {
    /** The parent node of this node. Is null if destroyed or if is the root. */
    parent: TreeNode | null;
    /** The key of this node. */
    readonly key: string;
    /** The level of this node. Root has level -1 */
    readonly level: number;
    /** Contains all the children by their key */
    private children;
    /**
     * The head of the singly linked list of direct children nodes that are invalidated and need to be committed.
     * We use this so we can invalidate just the path and explore only the invalidated during commit.
     * Also, once a path is invalidated the next invalidation will not add the same node again and stop the recursion quickly.
     */
    private invalidatedHead;
    /**
     * The next node in the linked list of parent.invalidatedHead.
     * - undefined: the node is not invalidated (not present in the parent linked list)
     * - null: this is the first and last node in the linked list
     * - TreeNode instance: is the next node in the linked list
     */
    private invalidatedNext;
    /** The RowNode associated to this tree node */
    row: TreeRow | null;
    /** We use this during commit to understand if the row changed. After commit, it will be the same as this.row. */
    oldRow: TreeRow | null;
    /**
     * There may be duplicate rows if they have the same key.
     * This is NOT an edge case, temporarily duplicates may arise during transactions.
     * For example, think about swapping the paths of two nodes, they will have the same key for a short while.
     */
    duplicateRows: Set<TreeRow> | null;
    /** We keep the row.childrenAfterGroup here, we just swap arrays when we assign rows */
    childrenAfterGroup: TreeRow[];
    /**
     * We keep the row.allLeafChildren here, we just swap arrays when we assign or swap the row to this node.
     * If this is null, we are borrowing the allLeafChildren array from one of the children,
     * in this case the row.allLeafChildren will be the same as one of the childrenAfterGroup[x].allLeafChildren,
     * to get the allLeafChildren if is null, do node.allLeafChildren ?? node.row.allLeafChildren.
     */
    allLeafChildren: TreeRow[] | null;
    /** Indicates whether childrenAfterGroup might need to be recomputed and sorted. Reset during commit. */
    childrenChanged: boolean;
    /** Indicates whether allLeafChildren should be recomputed. Reset to false during commit. */
    leafChildrenChanged: boolean;
    /** This is set if the duplicate key warning was already raised for this node, to reduce the performance hit */
    duplicateRowsWarned?: boolean;
    /** The ordering this node had in the previous commit. */
    sourceIdx: number;
    constructor(
    /** The parent node of this node. Is null if destroyed or if is the root. */
    parent: TreeNode | null, 
    /** The key of this node. */
    key: string, 
    /** The level of this node. Root has level -1 */
    level: number);
    /** Returns the number of children in this node */
    get size(): number;
    isEmptyFillerNode(): boolean;
    /** Returns an iterator able to iterate all children in this node, in order of insertion */
    enumChildren(): IterableIterator<TreeNode>;
    /**
     * Gets a node a key in the given parent. If the node does not exists, creates a filler node, with null row.
     * We cast to string just to be sure the user passed a string correctly and not a number or something else.
     * @param key - The key of the node to get.
     * @param append - If true, the node will be moved to the end of the children list.
     * @returns the node at the given key, or a new filler node inserted there if it does not exist.
     */
    upsertKey(key: string | number): TreeNode;
    /** Same as upsertKey, but moves the node to the end no matter what. */
    appendKey(key: string | number): TreeNode;
    /** Removes this node from the parent, and free memory. This node cannot be used after this. */
    destroy(): void;
    /**
     * Sets the row for the TreeNode.
     * If the row is already set, it will be replaced with the new row, and the old row will be orphaned.
     * childrenAfterGroup and allLeafChildren will be reassigned.
     * @returns True if the row changed
     */
    setRow(newRow: TreeRow | null): boolean;
    /**
     * Removes a row from the tree node.
     * If the row is the main row, it will be replaced with the first row in the duplicate rows, if any.
     * If the row is a duplicate row, it will be removed from the duplicate rows.
     * @param rowToRemove - The row to be removed.
     * @returns `true` if the row was successfully removed, `false` if the row was not found.
     */
    removeRow(rowToRemove: TreeRow): boolean;
    /**
     * Adds a duplicate row to the tree node.
     * @param newRow - The new row to be added.
     * @returns A boolean indicating whether the row was successfully added.
     */
    addDuplicateRow(newRow: TreeRow): boolean;
    /**
     * This is needed to be sure that the row is the duplicate row with the smallest sourceRowIndex, in O(n).
     * @returns this.row
     */
    sortFirstDuplicateRow(): TreeRow | null;
    /** Pops the first duplicate row from the list of duplicates */
    private popDuplicateRow;
    /**
     * Dequeues the next child invalidated node to be committed. Order is not deterministic.
     * @returns the next child node to be committed, or null if all children were already dequeued.
     */
    dequeueInvalidated(): TreeNode | null;
    /**
     * Invalidates this node and all its parents until the root is reached.
     * Order of invalidated nodes is not deterministic.
     * The root itself cannot be invalidated, as it has no parents.
     * If a node is already invalidated, it will stop the recursion.
     */
    invalidate(): void;
    /** Marks childrenChanged in the parent, so the childrenAfterGroup will be recomputed and invalidates the parent. */
    invalidateOrder(): void;
    /**
     * When we receive rowNodeOrder not undefined, we need to update the rowPosition of the node,
     * to ensure it will be sorted in the right order in childrenAfterGroup.
     * This function makes sense to be called only in the post-order commit DFS
     * as it assumes children's childrenAfterGroup is already updated.
     * @returns the rowPosition the node should have.
     */
    getNewSourceIdx(): number;
    /**
     * This is called in post order during commit to update the childrenAfterGroup array.
     * It uses the rowNodeOrder map to sort the children in the right order, if is passed.
     * It assumes all children childrenAfterGroup are up to date and rows all created.
     *
     * It replaces the array with _EmptyArray if there are no children, to reduce memory usage and GC pressure.
     * It does sort the children only if strictly needed, to avoid unnecessary work.
     *
     * If the order changes, also the order in the children map will be updated,
     * so the next call to enumChildren() will return the children in the right order.
     */
    updateChildrenAfterGroup(treeData: boolean): boolean;
    /** This reorders the given array and rebuild the children map. */
    private reorderChildrenList;
    /**
     * Rebuild the allLeafChildren rows array of a node. It uses childrenAfterGroup, we assume to be already updated.
     * This is called in post order during commit, after the childrenAfterGroup are updated with updateChildrenAfterGroup().
     * It uses the childrenAfterGroup and allLeafChildren of all the children, we assume they are updated.
     */
    updateAllLeafChildren(): void;
}
