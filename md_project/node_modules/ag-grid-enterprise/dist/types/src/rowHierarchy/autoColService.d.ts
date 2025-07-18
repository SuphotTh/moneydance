import type { ColKey, ColumnEventType, IAutoColService, NamedBean, _ColumnCollections } from 'ag-grid-community';
import { AgColumn, BeanStub } from 'ag-grid-community';
export declare class AutoColService extends BeanStub implements NamedBean, IAutoColService {
    beanName: "autoColSvc";
    autoCols: _ColumnCollections | null;
    postConstruct(): void;
    addAutoCols(cols: _ColumnCollections): void;
    createAutoCols(cols: _ColumnCollections, updateOrders: (callback: (cols: AgColumn[] | null) => AgColumn[] | null) => void): void;
    getAutoCol(key: ColKey): AgColumn | null;
    getAutoCols(): AgColumn[] | null;
    private generateAutoCols;
    updateAutoCols(source: ColumnEventType): void;
    private isSuppressAutoCol;
    private createOneAutoCol;
    /**
     * Refreshes an auto group col to load changes from defaultColDef or autoGroupColDef
     */
    private updateOneAutoCol;
    private createAutoColDef;
    private createBaseColDef;
    private onAutoGroupColumnDefChanged;
    destroy(): void;
}
