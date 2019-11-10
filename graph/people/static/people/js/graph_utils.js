class GraphDataPreprocessor {
    constructor(graph, enums) {
        this.graph = graph;

        this.relationshipColors = {
            [enums.relationships.bloodRelative]: '#008080',
            [enums.relationships.sibling]: '#008700',
            [enums.relationships.parentChild]: '#8080ff',
            [enums.relationships.married]: '#b70000',
            [enums.relationships.engaged]: '#ffc000',
            [enums.relationships.dating]: '#ffffff',
            [enums.relationships.rumour]: '#ff00ff',
        };
        this.seminarColors = {
            [enums.seminars.KSP]: '#818f3d',
            [enums.seminars.KMS]: '#4a6fd8',
            [enums.seminars.FKS]: '#e39f3c',
        };

        this.graph.nodes.forEach((node) => {
            node.displayProps = {};
            this.preprocessNode(node);
        });
        this.graph.edges.forEach((edge) => {
            edge.displayProps = {};
            this.preprocessEdge(edge);
        });
    }

    preprocessNode(node) {
        node.memberships.map((membership) => {
            membership.date_started = new Date(membership.date_started);
            membership.date_ended = membership.date_ended ? new Date(membership.date_ended) : null
        });
        node.seminar_memberships = node.memberships.filter((membership) => {
            return (this.seminarColors.hasOwnProperty(membership.group_name) && (membership.duration > 0))
        });
        const cumulativeDuration = node.seminar_memberships.map((m) => m.duration).reduce((acc, val) => acc + val, 0);

        node.displayProps.pie = [];
        let previousAngleEnd = 0;
        node.seminar_memberships.forEach((membership) => {
            const angleEnd = previousAngleEnd + membership.duration / cumulativeDuration * Math.PI * 2;
            node.displayProps.pie.push({
                angleStart: previousAngleEnd,
                angleEnd: angleEnd,
                color: this.seminarColors[membership.group_name]
            });
            previousAngleEnd = angleEnd;
        });

        node.displayProps.label = node.nickname ? node.nickname : node.first_name + ' ' + node.last_name;
        node.displayProps.radius = 3 + Math.ceil(Math.sqrt(node.age * 2))
    }

    preprocessEdge(edge) {
        const sorted_statuses = edge.statuses.map((status) => {
            status.date_start = new Date(status.date_start);
            status.date_end = status.date_end ? new Date(status.date_end): null;
            return status
        }).sort((a, b) => a.date_start < b.date_start ? 1 : -1);
        edge.newest_status = sorted_statuses[0];

        edge.displayProps.dashing = edge.newest_status.date_end ? [2, 2]: [];
        edge.displayProps.width = edge.newest_status.date_end ? 1: Math.ceil(Math.log(Math.sqrt(edge.newest_status.days_together / 10)));
        edge.displayProps.color = this.relationshipColors[edge.newest_status.status]
    }
}

class GraphRenderer {
    constructor(graph, canvas) {
        this.graph = graph;
        this.canvas = canvas;
        this.context = this.canvas.getContext('2d');
    }

    renderEdge = (edge) => {
        this.context.save();
        this.context.beginPath();
        this.context.lineWidth = edge.displayProps.width;
        this.context.strokeStyle = edge.displayProps.color;
        this.context.setLineDash(edge.displayProps.dashing);
        this.context.moveTo(edge.source.x, edge.source.y);
        this.context.lineTo(edge.target.x, edge.target.y);
        this.context.stroke();
        this.context.restore();
    };

    renderNode = (node) => {
        this.context.save();
        this.context.beginPath();
        this.context.lineWidth = 2;
        this.context.arc(node.x, node.y, node.displayProps.radius, 0, 2 * Math.PI, true);
        if (node.displayProps.selected){
            this.context.strokeStyle = '#fff'
        }
        this.context.stroke();
        if (node.displayProps.pie.length > 0) {
            node.displayProps.pie.forEach((section) => {
                this.context.beginPath();
                this.context.moveTo(node.x, node.y);
                this.context.arc(node.x, node.y, node.displayProps.radius, section.angleStart, section.angleEnd, true);
                this.context.fillStyle = section.color;
                this.context.fill();
            });
        } else {
            this.context.fillStyle = '#666';
            this.context.fill();
        }
        this.context.fillStyle = "#FFF";
        this.context.fillText(
            node.displayProps.label,
            node.x - this.context.measureText(node.displayProps.label).width / 2,
            node.y - node.displayProps.radius - 2
        );
        this.context.restore();
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
    constructor(graph, canvas){
        this.canvas = canvas;
        this.simulation = d3.forceSimulation()
            .force("center", d3.forceCenter(this.canvas.width / 2, this.canvas.height / 2))
            .force("collide", d3.forceCollide())
            .force("x", d3.forceX(this.canvas.width / 2).strength(0.04))
            .force("y", d3.forceY(this.canvas.height / 2).strength(0.04))
            .force("charge", d3.forceManyBody().strength(-200))
            .force("link", d3.forceLink().strength(0.3).id((node) => node.id))
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

        this.render = () => {};
        this.transform = d3.zoomIdentity;
        this.simulation.on("tick", this.update);
    }

    update = () => {
        this.render(this.transform);
    };

    nodeOnMousePosition = (mouseX, mouseY) => {
        let i, dx, dy, x = this.transform.invertX(mouseX), y = this.transform.invertY(mouseY);
        for (i = 0; i < this.graph.nodes.length; ++i){
            const node = this.graph.nodes[i];
            dx = x - node.x;
            dy = y - node.y;
            if (dx * dx + dy * dy < node.displayProps.radius * node.displayProps.radius){
                return node
            }
        }
    };

    zoomed = () => {
        this.transform = d3.event.transform;
        this.update()
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

function dateToString(date, now_when_null=true){
    const dateOpt = {year: 'numeric', month: 'numeric', day: 'numeric'};
    return date ? date.toLocaleString('sk-SK', dateOpt) : (now_when_null ? 'Now' : '')
}
