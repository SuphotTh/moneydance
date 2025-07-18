import type { IFooterService, NamedBean, RowNode } from 'ag-grid-community';
import { BeanStub } from 'ag-grid-community';
export declare class FooterService extends BeanStub implements NamedBean, IFooterService {
    beanName: "footerSvc";
    addNodes(params: {
        index: number;
    }, nodes: RowNode[], callback: (node: RowNode, index: number) => void, includeFooterNodes: boolean, rootNode: RowNode | null, position: 'top' | 'bottom'): void;
    getTopDisplayIndex(rowsToDisplay: RowNode[], topLevelIndex: number, childrenAfterSort: RowNode[], getDefaultIndex: (adjustedIndex: number) => number): number;
}
