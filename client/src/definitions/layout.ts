import type Led from "./led";

export default class Layout {
    public leds: Led[];
    public xMin: number;
    public yMin: number;
    public xMax: number;
    public yMax: number;

    constructor(leds: Led[], xMin: number, yMin: number, xMax: number, yMax: number) {
        this.leds = leds;
        this.xMin = xMin;
        this.yMin = yMin;
        this.xMax = xMax;
        this.yMax = yMax;
    }
}