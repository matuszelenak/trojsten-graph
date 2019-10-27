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
        // Create pie chart showing the ratio of seminar membership durations
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

        if (node.nick === 'Paťo'){
            console.log(node);
        }

        node.display_props.label = node.nick;
        node.display_props.radius = 5 + Math.ceil(Math.log(node.age + 1))
    }

    preprocessEdge(edge) {
        edge.display_props.dashing = edge.status.is_active ? [] : [2, 2];
        edge.display_props.width = edge.status.is_active ? Math.ceil(Math.log(Math.sqrt(edge.status.days_together / 30))) : 1;
    }
}


class GraphRenderer {
    constructor(graph, context) {
        this.graph = graph;
        this.context = context;
    }

    renderEdge(edge) {
        this.context.beginPath();
        this.context.lineWidth = edge.display_props.width;
        this.context.strokeStyle = '#ccc';
        this.context.setLineDash(edge.display_props.dashing);
        this.context.moveTo(edge.source.x, edge.source.y);
        this.context.lineTo(edge.target.x, edge.target.y);
        this.context.stroke();
    }

    renderNode(node) {
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
            node.x - context.measureText(node.display_props.label).width / 2,
            node.y - node.display_props.radius - 2
        );
    }

    renderGraph() {
        this.graph.edges.forEach((edge) => {
            this.renderEdge(edge);
        });
        this.context.font = "normal normal bold 12px sans-serif";
        this.graph.nodes.forEach((node) => {
            this.renderNode(node);
        });
    }
}