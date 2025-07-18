import { _ModuleSupport } from 'ag-charts-community';
type ShapeClipMask = {
    x: number;
    y: number;
    radius: number;
};
export declare class CollidableLine extends _ModuleSupport.Line {
    collisionBBox?: _ModuleSupport.BBox;
    private readonly growCollisionBox;
    protected clipMask: Map<string, ShapeClipMask>;
    setProperties<T>(styles: {
        [K in keyof T]?: T[K] | undefined;
    }, pickKeys?: (keyof T)[]): T;
    private updateCollisionBBox;
    isPointInPath(pointX: number, pointY: number): boolean;
    render(renderCtx: _ModuleSupport.RenderContext): void;
    setClipMask(id: string, mask?: ShapeClipMask): void;
    /**
     * Apply a clipping mask to the shape, this must be called before the shape calls `ctx.beginPath()`.
     */
    protected applyClipMask(ctx: CanvasRenderingContext2D | OffscreenCanvasRenderingContext2D): void;
    protected closeClipMask(ctx: CanvasRenderingContext2D | OffscreenCanvasRenderingContext2D): void;
}
export {};
