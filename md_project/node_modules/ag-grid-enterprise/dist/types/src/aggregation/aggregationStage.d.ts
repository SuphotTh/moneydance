import type { AgColumn, BeanCollection, ClientSideRowModelStage, GridOptions, IAggFunc, IRowNodeStage, NamedBean, RowNode, StageExecuteParams } from 'ag-grid-community';
import { BeanStub } from 'ag-grid-community';
export declare class AggregationStage extends BeanStub implements NamedBean, IRowNodeStage {
    beanName: "aggStage";
    refreshProps: Set<keyof GridOptions<any>>;
    step: ClientSideRowModelStage;
    private colModel;
    private valueSvc;
    private aggFuncSvc;
    private pivotColsSvc?;
    private valueColsSvc?;
    private pivotResultCols?;
    wireBeans(beans: BeanCollection): void;
    execute(params: StageExecuteParams): any;
    private createAggDetails;
    private isSuppressAggFilteredOnly;
    private recursivelyCreateAggData;
    private aggregateRowNode;
    private aggregateRowNodeUsingValuesAndPivot;
    private aggregateRowNodeUsingValuesOnly;
    private getValuesPivotNonLeaf;
    private getValuesFromMappedSet;
    private getValuesNormal;
    aggregateValues(values: any[], aggFuncOrString: string | IAggFunc, column?: AgColumn, rowNode?: RowNode, pivotResultColumn?: AgColumn): any;
    private setAggData;
}
