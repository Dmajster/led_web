import Layout from "./layout";
import Led from "./led";
import type Segment from "./segment";
import Vec2 from "./vec2";

export default class Strip {
    public name: string;
    public segments: Segment[];
    public template: string | ArrayBuffer | null;
    public templateScale: number;
    public lengthMeters: number;
    public totalLeds: number;
    public layout: Layout | null;

    constructor() {
        this.name = 'Unnamed strip';
        this.segments = [];
        this.template = null;
        this.templateScale = 1;
        this.lengthMeters = 3;
        this.totalLeds = 180;
        this.layout = null;
    }

    addSegment(segment: Segment) {
        this.segments = [...this.segments, segment];
    }

    createLayout() {
        let xMin = Number.MAX_VALUE;
        let yMin = Number.MAX_VALUE;
        let xMax = Number.MIN_VALUE;
        let yMax = Number.MIN_VALUE;
        let leds = [];

        for (var segment of this.segments) {
            if (segment.points.length == 0) {
                continue;
            }
            let pointIndex = 0;
            let point = segment.points[pointIndex];
            let nextPoint = segment.points[pointIndex + 1];
            let distanceToPoint = 0;
            let distanceToNextPoint = Vec2.distance(point, nextPoint);
            let direction = Vec2.direction(point, nextPoint);
            let steppedDistance = 0;
            let step = this.templateScale;
            let ledIndex = 0;
            while (true) {
                steppedDistance += step;

                if (steppedDistance > distanceToNextPoint) {
                    pointIndex++;

                    if (pointIndex + 1 == segment.points.length) {
                        break;
                    }

                    point = segment.points[pointIndex];
                    nextPoint = segment.points[pointIndex + 1];

                    distanceToPoint = distanceToNextPoint;
                    distanceToNextPoint = distanceToPoint + Vec2.distance(point, nextPoint);

                    direction = Vec2.direction(point, nextPoint);
                }

                let x = point.x + direction.x * (steppedDistance - distanceToPoint);
                let y = point.y + direction.y * (steppedDistance - distanceToPoint);
                leds.push(new Led(ledIndex, x, y))
                ledIndex++;

                if (x < xMin) {
                    xMin = x;
                }
                if (x > xMax) {
                    xMax = x;
                }
                if (y < yMin) {
                    yMin = y;
                }
                if (y > yMax) {
                    yMax = y;
                }
            }
        }

        this.layout = new Layout(leds, xMin, yMin, xMax, yMax);
    }
}