import { AbstractSelectionHandle, SelectionHandleType } from './abstractSelectionHandle';
export declare class AgRangeHandle extends AbstractSelectionHandle {
    protected type: SelectionHandleType;
    private endPosition;
    private rangeFixed;
    constructor();
    protected onDrag(_: MouseEvent): void;
    protected onDragEnd(_: MouseEvent): void;
    protected onDragCancel(): void;
    private fixRangeStartEnd;
}
