import { BeanStub } from 'ag-grid-community';
import type { VirtualList } from '../widgets/virtualList';
import type { AgPrimaryColsList } from './agPrimaryColsList';
export declare class PrimaryColsListPanelItemDragFeature extends BeanStub {
    private readonly comp;
    private readonly virtualList;
    constructor(comp: AgPrimaryColsList, virtualList: VirtualList);
    postConstruct(): void;
    private getCurrentDragValue;
    private getCurrentColumnsBeingMoved;
    private isMoveBlocked;
    private moveItem;
    private getMoveTargetIndex;
    private getMoveDiff;
}
