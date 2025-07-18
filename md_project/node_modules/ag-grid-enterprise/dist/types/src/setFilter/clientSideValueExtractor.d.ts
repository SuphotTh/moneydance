import type { AgEventType, IClientSideRowModel, IColsService, RowNode, SetFilterParams, ValueService } from 'ag-grid-community';
import { AgPromise } from 'ag-grid-community';
/** @param V type of value in the Set Filter */
export declare class ClientSideValuesExtractor<V> {
    private readonly rowModel;
    private readonly filterParams;
    private readonly createKey;
    private readonly caseFormat;
    private readonly valueSvc;
    private readonly treeDataOrGrouping;
    private readonly treeData;
    private readonly groupAllowUnbalanced;
    private readonly addManagedEventListeners;
    private readonly rowGroupColsSvc?;
    constructor(rowModel: IClientSideRowModel, filterParams: SetFilterParams<any, V>, createKey: (value: V | null | undefined, node?: RowNode) => string | null, caseFormat: <T extends string | null>(valueToFormat: T) => typeof valueToFormat, valueSvc: ValueService, treeDataOrGrouping: boolean, treeData: boolean, groupAllowUnbalanced: boolean, addManagedEventListeners: (handlers: Partial<Record<AgEventType, (event?: any) => void>>) => (() => null)[], rowGroupColsSvc?: IColsService | undefined);
    extractUniqueValuesAsync(predicate: (node: RowNode) => boolean, existingValues?: Map<string | null, V | null>): AgPromise<Map<string | null, V | null>>;
    extractUniqueValues(predicate: (node: RowNode) => boolean, existingValues?: Map<string | null, V | null>): Map<string | null, V | null>;
    private addValueForTreeDataOrGrouping;
    private getValue;
    private extractExistingFormattedKeys;
}
