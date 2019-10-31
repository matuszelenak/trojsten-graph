class GraphDataPreprocessor {
    constructor(graph, enums) {
        this.graph = graph;
        this.enums = enums;

        this.graph.nodes.forEach((node) => {
            node.display_props = {};
            this.preprocessNode(node);
        });
        this.graph.edges.forEach((edge) => {
            edge.display_props = {};
            this.preprocessEdge(edge);
        });
    }

    seminar_to_color(seminar) {
        if (seminar === 'KSP') {
            return '#818f3d'
        } else if (seminar === 'KMS') {
            return '#4a6fd8'
        } else if (seminar === 'FKS') {
            return '#e39f3c'
        }
        return '#555'
    }

    preprocessNode(node) {
        const cumulative_duration = node
            .seminar_memberships
            .map((m) => m.duration)
            .reduce((acc, val) => acc + val, 0);

        node.display_props.pie = [];
        let previous_angle_end = 0;
        node.seminar_memberships.forEach((membership) => {
            const angle_end = previous_angle_end + membership.duration / cumulative_duration * Math.PI * 2;
            node.display_props.pie.push({
                angle_start: previous_angle_end,
                angle_end: angle_end,
                color: this.seminar_to_color(membership.group)
            });
            previous_angle_end = angle_end;
        });

        node.display_props.label = node.nick;
        node.display_props.radius = 3 + Math.ceil(Math.sqrt(node.age * 2))
    }

    preprocessEdge(edge) {
        edge.display_props.dashing = edge.status.is_active ? [] : [2, 2];
        edge.display_props.width = edge.status.is_active ? Math.ceil(Math.log(Math.sqrt(edge.status.days_together / 10))) : 1;
    }
}

class GraphRenderer {
    constructor(graph, canvas) {
        this.graph = graph;
        this.canvas = canvas;
        this.context = this.canvas.getContext('2d');
    }

    renderEdge = (edge) => {
        this.context.beginPath();
        this.context.lineWidth = edge.display_props.width;
        this.context.strokeStyle = '#ccc';
        this.context.setLineDash(edge.display_props.dashing);
        this.context.moveTo(edge.source.x, edge.source.y);
        this.context.lineTo(edge.target.x, edge.target.y);
        this.context.stroke();
    };

    renderNode = (node) => {
        this.context.beginPath();
        this.context.lineWidth = 2;
        this.context.arc(node.x, node.y, node.display_props.radius, 0, 2 * Math.PI, true);
        this.context.stroke();
        if (node.display_props.pie.length > 0) {
            node.display_props.pie.forEach((section) => {
                this.context.beginPath();
                this.context.moveTo(node.x, node.y);
                this.context.arc(node.x, node.y, node.display_props.radius, section.angle_start, section.angle_end, true);
                this.context.fillStyle = section.color;
                this.context.fill();
            });
        } else {
            this.context.fillStyle = '#666';
            this.context.fill();
        }
        this.context.fillStyle = "#FFF";
        this.context.fillText(
            node.display_props.label,
            node.x - this.context.measureText(node.display_props.label).width / 2,
            node.y - node.display_props.radius - 2
        );
    };

    renderGraph = (transform) => {
        this.context.save();
        this.context.fillStyle = '#222';
        this.context.fillRect(0, 0, this.canvas.width, this.canvas.height);
        this.context.translate(transform.x, transform.y);
        this.context.scale(transform.k, transform.k);

        this.graph.edges.forEach((edge) => {
            this.renderEdge(edge);
        });
        this.context.font = "normal normal bold 12px sans-serif";
        this.graph.nodes.forEach((node) => {
            this.renderNode(node);
        });

        this.context.restore();
    }
}


class GraphSimulation {
    constructor(canvas, graph, renderer){
        this.canvas = canvas;
        this.simulation = d3.forceSimulation()
            .force("center", d3.forceCenter(this.canvas.width / 2, this.canvas.height / 2))
            .force("collide", d3.forceCollide())
            .force("x", d3.forceX(this.canvas.width / 2).strength(0.05))
            .force("y", d3.forceY(this.canvas.height / 2).strength(0.05))
            .force("charge", d3.forceManyBody().strength(-150))
            .force("link", d3.forceLink().strength(0.4).id((node) => node.id))
            .alphaTarget(0)
            .alphaDecay(0.05);

        d3.select(this.canvas)
            .call(d3.drag().subject(this.dragsubject)
                .on("start", this.dragstarted)
                .on("drag", this.dragged)
                .on("end", this.dragended))
            .call(d3.zoom().scaleExtent([1 / 10, 8]).on("zoom", this.zoomed));

        this.graph = graph;
        this.simulation.nodes(graph.nodes);
        this.simulation.force("link").links(graph.edges);

        this.renderer = renderer;
        this.transform = d3.zoomIdentity;
        this.simulation.on("tick", () => {
            this.renderer.renderGraph(this.transform);
        });
    }

    nodeOnMousePosition = (mouse_x, mouse_y) => {
        let i, dx, dy, x = this.transform.invertX(mouse_x), y = this.transform.invertY(mouse_y);
        for (i = 0; i < this.graph.nodes.length; ++i){
            const node = this.graph.nodes[i];
            dx = x - node.x;
            dy = y - node.y;
            if (dx * dx + dy * dy < node.display_props.radius * node.display_props.radius){
                return node
            }
        }
    };

    zoomed = () => {
        this.transform = d3.event.transform;
        this.renderer.renderGraph(this.transform);
    };

    dragsubject = () => {
        const node = this.nodeOnMousePosition(d3.event.x, d3.event.y);
        if (node) {
            node.x = this.transform.applyX(node.x);
            node.y = this.transform.applyY(node.y);
            return node
        }
    };

    dragstarted = () => {
        if (!d3.event.active) this.simulation.alphaTarget(0.3).restart();
        d3.event.subject.fx = this.transform.invertX(d3.event.x);
        d3.event.subject.fy = this.transform.invertY(d3.event.y);
    };

    dragged = () => {
        d3.event.subject.fx = this.transform.invertX(d3.event.x);
        d3.event.subject.fy = this.transform.invertY(d3.event.y);
    };

    dragended = () => {
        if (!d3.event.active) this.simulation.alphaTarget(0);
        d3.event.subject.fx = null;
        d3.event.subject.fy = null;
    }
}