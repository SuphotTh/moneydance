import { type AgChartLegendPosition, type AgGradientLegendScaleOptions, _ModuleSupport } from 'ag-charts-community';
declare const BaseProperties: typeof _ModuleSupport.BaseProperties;
declare class GradientBar extends BaseProperties {
    thickness: number;
    preferredLength: number;
}
declare class GradientLegendScale implements AgGradientLegendScaleOptions {
    protected axisTicks: _ModuleSupport.AxisTicks;
    constructor(axisTicks: _ModuleSupport.AxisTicks);
    label: _ModuleSupport.AxisLabel;
    interval: _ModuleSupport.AxisInterval<number>;
    padding?: _ModuleSupport.AxisTicks['padding'];
}
export declare class GradientLegend {
    readonly ctx: _ModuleSupport.ModuleContext;
    static readonly className = "GradientLegend";
    readonly id: string;
    private readonly axisTicks;
    private readonly highlightManager;
    private readonly legendGroup;
    private readonly gradientRect;
    private readonly arrow;
    private readonly ticksGroup;
    private readonly destroyFns;
    enabled: boolean;
    position: AgChartLegendPosition;
    reverseOrder: boolean;
    readonly gradient: GradientBar;
    private isVertical;
    /**
     * Spacing between the legend and the edge of the chart's element.
     */
    spacing: number;
    scale: GradientLegendScale;
    data: _ModuleSupport.GradientLegendDatum[];
    constructor(ctx: _ModuleSupport.ModuleContext);
    destroy(): void;
    attachLegend(scene: _ModuleSupport.Scene): void;
    private onStartLayout;
    private normalizeColorArrays;
    private updateGradientRect;
    private updateAxis;
    private updateArrow;
    private getMeasurements;
    private onChartHoverChange;
}
export {};
