import type { BeanCollection } from 'ag-grid-community';
import { Component } from 'ag-grid-community';
export type InputPillCompEvent = 'fieldValueChanged';
export declare class InputPillComp extends Component<InputPillCompEvent> {
    private readonly params;
    private advFilterExpSvc;
    wireBeans(beans: BeanCollection): void;
    private readonly ePill;
    private readonly eLabel;
    private eEditor;
    private value;
    private displayValue;
    constructor(params: {
        value: string;
        valueFormatter: (value: string) => string;
        cssClass: string;
        type: 'text' | 'number' | 'date';
        ariaLabel: string;
    });
    postConstruct(): void;
    getFocusableElement(): HTMLElement;
    private showEditor;
    private createEditorComp;
    private hideEditor;
    private renderValue;
    private updateValue;
}
