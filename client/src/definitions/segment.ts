import type Vec2 from "./vec2";

export default class Segment {
    public name: string;
    public points: Vec2[];

    constructor() {
        this.name = 'Unnamed segment';
        this.points = [];
    }

    addPoint(point: Vec2) {
        this.points = [...this.points, point];
    }
}