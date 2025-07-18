import type { AgCrosshairLabelRendererParams, AgCrosshairLabelRendererResult } from 'ag-charts-community';
import { _ModuleSupport } from 'ag-charts-community';
declare const BaseProperties: typeof _ModuleSupport.BaseProperties;
export declare class CrosshairLabelProperties extends _ModuleSupport.ChangeDetectableProperties {
    enabled: boolean;
    xOffset: number;
    yOffset: number;
    format?: string;
    renderer?: (params: AgCrosshairLabelRendererParams) => string | AgCrosshairLabelRendererResult;
}
export declare class CrosshairLabel extends BaseProperties {
    private readonly domManager;
    private readonly id;
    enabled: boolean;
    xOffset: number;
    yOffset: number;
    format?: string;
    renderer?: (params: AgCrosshairLabelRendererParams) => string | AgCrosshairLabelRendererResult;
    private readonly element;
    constructor(domManager: _ModuleSupport.DOMManager, key: string, axisId: string);
    show(meta: _ModuleSupport.Point): void;
    setLabelHtml(html?: string): void;
    getBBox(): _ModuleSupport.BBox;
    toggle(visible?: boolean): void;
    destroy(): void;
    toLabelHtml(input: string | AgCrosshairLabelRendererResult, defaults?: AgCrosshairLabelRendererResult): string;
}
export {};
