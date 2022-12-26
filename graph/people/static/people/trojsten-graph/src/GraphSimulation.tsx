import * as d3 from "d3";
import {ForceLink, Simulation, ZoomTransform} from "d3";
import { chain } from "lodash";
import {Graph, GraphEdge, GraphNode} from "./Graph";
import {GraphView} from "./GraphView";
import {distToSegment} from "./Utils";

export class GraphSimulation {
    private canvas: HTMLCanvasElement;
    private simulation: Simulation<GraphNode, GraphEdge>;
    private transformation: ZoomTransform;
    public graphView: GraphView;
    private readonly updateCallback: (graph: GraphView, transform: ZoomTransform) => void;

    constructor(canvas: HTMLCanvasElement, updateCallback: (graph: GraphView, transform: ZoomTransform) => void) {
        this.canvas = canvas
        this.updateCallback = updateCallback

        this.graphView = new GraphView([], [])

        this.simulation = d3.forceSimulation<GraphNode, GraphEdge>()
            .force("center", d3.forceCenter(this.canvas.width / 2, this.canvas.height / 2))
            .force("collide", d3.forceCollide())
            .force("x", d3.forceX(this.canvas.width / 2).strength(0.04))
            .force("y", d3.forceY(this.canvas.height / 2).strength(0.04))
            .force("charge", d3.forceManyBody<GraphNode>().strength(-300))
            .force("link", d3.forceLink<GraphNode, GraphEdge>().strength(0.2).id(node => node.id))

        const dragBehaviour = d3.drag()
            .subject(this.dragSubject)
            .on("start", this.dragStarted)
            .on("drag", this.dragged)
            .on("end", this.dragEnded)

        const zoomBehaviour = d3.zoom().scaleExtent([1 / 10, 8])
            .on("zoom", (e) => {
                this.transformation = e.transform
                this.update()
            })

        // @ts-ignore
        d3.select(canvas).call(dragBehaviour).call(zoomBehaviour)
            .on("mousemove", this.mouseMove)
            .on("click", this.mouseClick)

        this.transformation = d3.zoomIdentity
        this.simulation.on("tick", this.update)
    }

    update = () => {
        this.graphView.nodes.forEach(node => {
            node.displayX = ~~(node.x || 0)
            node.displayY = ~~(node.y || 0)
        })
        this.updateCallback(this.graphView, this.transformation)
    }

    setData = (graph: GraphView) => {
        this.graphView = graph

        this.simulation.nodes(this.graphView.nodes);
        (this.simulation.force("link") as ForceLink<GraphNode, GraphEdge>).links(this.graphView.edges)
        this.simulation.alphaTarget(0.1).alphaDecay(0.01).restart();
    }

    nodeOnMousePosition = (mouseX: number, mouseY: number): GraphNode | null => {
        let dx, dy, x = this.transformation.invertX(mouseX), y = this.transformation.invertY(mouseY);
        for (const node of this.graphView.nodes) {
            // @ts-ignore
            dx = x - node.x;
            // @ts-ignore
            dy = y - node.y;
            if (dx * dx + dy * dy < node.displayProps.radius * node.displayProps.radius) {
                return node
            }
        }
        return null
    };

    edgeOnMousePosition = (mouseX: number, mouseY: number): GraphEdge | null => {
        let x = this.transformation.invertX(mouseX), y = this.transformation.invertY(mouseY);
        const nodeXs = chain(this.graphView.nodes).keyBy('id').mapValues('x').value()
        const nodeYs = chain(this.graphView.nodes).keyBy('id').mapValues('y').value()
        for (const edge of this.graphView.edges) {

            const d = distToSegment(
                {
                    x: x,
                    y: y
                },
                {
                    sx: nodeXs[edge.sourceId] as number,
                    sy: nodeYs[edge.sourceId] as number,
                    ex: nodeXs[edge.targetId] as number,
                    ey: nodeYs[edge.targetId] as number
                }
            )
            if (d < 5) {
                return edge
            }
        }

        return null
    }

    mouseMove = (event: MouseEvent) => {
        // const target = this.nodeOnMousePosition(event.x, event.y)
        // if (target !== null) {
        //     this.canvas.style.cursor = "pointer"
        // } else {
        //     this.canvas.style.cursor = "default"
        // }

        const target = this.edgeOnMousePosition(event.x, event.y)
        if (target !== null) {
            this.canvas.style.cursor = "pointer"
        } else {
            this.canvas.style.cursor = "default"
        }

        this.update()
    }

    mouseClick = (event: MouseEvent) => {

    }

    dragSubject = (event: d3.D3DragEvent<any, any, any>) => {
        const node = this.nodeOnMousePosition(event.x, event.y);
        if (node !== null) {
            // @ts-ignore
            node.x = this.transformation.applyX(node.x);
            // @ts-ignore
            node.y = this.transformation.applyY(node.y);
            return node
        }
    }

    dragStarted = (event: d3.D3DragEvent<any, any, any>) => {
        if (!event.active) this.simulation.alphaTarget(0.3).restart()
        event.subject.fx = this.transformation.invertX(event.x)
        event.subject.fy = this.transformation.invertY(event.y)
    }

    dragged = (event: d3.D3DragEvent<any, any, any>) => {
        event.subject.fx = this.transformation.invertX(event.x)
        event.subject.fy = this.transformation.invertY(event.y)
    }

    dragEnded = (event: d3.D3DragEvent<any, any, any>) => {
        if (!event.active) this.simulation.alphaTarget(0)
        event.subject.fx = null
        event.subject.fy = null
    }

    focusViewOnNode = (node: GraphNode) => {
        this.transformation = this.transformation.translate(
            this.canvas.width / 2 - (node.x ?? 0),
            this.canvas.height / 2 - (node.y ?? 0)
        )
        this.update()
    }
}
