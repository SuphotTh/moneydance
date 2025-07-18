import type { BeanCollection, ColDef, ColGroupDef, IPivotColDefService, NamedBean } from 'ag-grid-community';
import { BeanStub } from 'ag-grid-community';
export interface PivotColDefServiceResult {
    pivotColumnGroupDefs: (ColDef | ColGroupDef)[];
    pivotColumnDefs: ColDef[];
}
export declare class PivotColDefService extends BeanStub implements NamedBean, IPivotColDefService {
    beanName: "pivotColDefSvc";
    private colModel;
    private pivotColsSvc?;
    private valueColsSvc?;
    private colNames;
    wireBeans(beans: BeanCollection): void;
    private fieldSeparator;
    private pivotDefaultExpanded;
    postConstruct(): void;
    createPivotColumnDefs(uniqueValues: any): PivotColDefServiceResult;
    private createPivotColumnsFromUniqueValues;
    private recursivelyBuildGroup;
    private buildMeasureCols;
    private addExpandablePivotGroups;
    private addPivotTotalsToGroups;
    private recursivelyAddPivotTotal;
    private addRowGroupTotals;
    private createColDef;
    private sameAggFuncs;
    private headerNameComparator;
    private merge;
    private generateColumnGroupId;
    private generateColumnId;
    /**
     * Used by the SSRM to create secondary columns from provided fields
     * @param fields
     */
    createColDefsFromFields(fields: string[]): (ColDef | ColGroupDef)[];
}
