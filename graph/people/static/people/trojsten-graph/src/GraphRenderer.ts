import {GraphEdge, GraphNode} from "./Graph";
import {ZoomTransform} from "d3";
import {defaultNodeColor} from "./Constants";
import {GraphView} from "./GraphView";

export class GraphRenderer {
    private canvas: HTMLCanvasElement;
    private context: CanvasRenderingContext2D;

    constructor(canvas: HTMLCanvasElement) {
        this.canvas = canvas
        this.context = canvas.getContext("2d") as CanvasRenderingContext2D
    }

    renderNode = (node: GraphNode) => {
        this.context.beginPath();

        if (node.displayProps.seminarPie.length > 0) {
            node.displayProps.seminarPie.forEach((section) => {
                this.context.beginPath();
                this.context.moveTo(node.displayX, node.displayY);
                this.context.arc(node.displayX, node.displayY, node.displayProps.radius, section.angleEnd, section.angleStart, true);
                this.context.fillStyle = section.color;
                this.context.fill();
            });
        } else {
            this.context.beginPath();
            this.context.arc(node.displayX, node.displayY, node.displayProps.radius, 0, 2 * Math.PI, true);
            this.context.fillStyle = defaultNodeColor;
            this.context.fill();
        }


        this.context.fillStyle = "#FFF";
        const displayName = node.person.nickname ?? `${node.person.firstName} ${node.person.lastName}`
        this.context.fillText(
            displayName,
            node.displayX - this.context.measureText(displayName).width / 2,
            node.displayY - 8
        );
        this.context.closePath()
    }

    renderEdge = (edge: GraphEdge) => {
        this.context.beginPath();
        this.context.lineWidth = edge.displayProps.width;
        this.context.strokeStyle = edge.displayProps.color;
        this.context.setLineDash(edge.displayProps.dashing);
        const source = edge.source as GraphNode
        const target = edge.target as GraphNode
        this.context.moveTo(source.displayX, source.displayY);
        this.context.lineTo(target.displayX, target.displayY);
        this.context.stroke();
        this.context.closePath()
    };

    renderGraph = (graph: GraphView, transform: ZoomTransform) => {
        this.context.save();
        this.context.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.context.translate(transform.x, transform.y);
        this.context.scale(transform.k, transform.k);

        graph.edges.forEach((edge) => {
            this.renderEdge(edge);
        });

        this.context.font = "normal normal bold 12px sans-serif";
        graph.nodes.forEach((node) => {
            this.renderNode(node);
        });

        this.context.restore();
    }
}
