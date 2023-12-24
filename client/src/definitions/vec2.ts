export default class Vec2 {
    public x: number;
    public y: number;

    constructor(x: number, y: number) {
        this.x = x;
        this.y = y;
    }

    static distance(v1: Vec2, v2: Vec2) {
        return Math.sqrt(Math.pow(v2.x - v1.x, 2) + Math.pow(v2.y - v1.y, 2));
    }

    static direction(v1: Vec2, v2: Vec2) {
        const distance = this.distance(v1, v2);
        return new Vec2((v2.x - v1.x) / distance, (v2.y - v1.y) / distance);
    }
}