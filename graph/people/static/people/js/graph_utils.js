function preprocessGraph(graph) {
    graph.nodes.forEach((node) => {
        stringsToDates(node, ['birth_date', 'death_date']);
        node.memberships.forEach((membership) => {
            stringsToDates(membership, ['date_started', 'date_ended']);
            membership.duration = timeDelta(membership.date_ended, membership.date_started).days
        });
        node.age = timeDelta(node.death_date, node.birth_date).years;
    });
    graph.edges.forEach((edge) => {
        edge.statuses.forEach((status) => {
            stringsToDates(status, ['date_start', 'date_end']);
            status.duration = timeDelta(status.date_end, status.date_start).days
        });
        edge.newest_status = edge.statuses[0];
    });
}

class GraphRenderer {
    constructor(graph, canvas) {
        this.graph = graph;
        this.canvas = canvas;
        this.context = this.canvas.getContext('2d');
        this.calculateDisplayProps()
    }

    nodeDisplayProps = (node) => {
        let props = {};
        const seminar_memberships = node.memberships.filter((membership) => {
            return (enums.seminarColors.hasOwnProperty(membership.group_name) && (membership.duration > 0))
        });

        props.pie = [];
        const cumulativeDuration = seminar_memberships.map((m) => m.duration).reduce((acc, val) => acc + val, 0);
        let previousAngleEnd = 0;
        seminar_memberships.forEach((membership) => {
            const angleEnd = previousAngleEnd + (membership.duration / cumulativeDuration) * Math.PI * 2;
            props.pie.push({
                angleStart: previousAngleEnd,
                angleEnd: angleEnd,
                color: enums.seminarColors[membership.group_name]
            });
            previousAngleEnd = angleEnd;
        });

        props.label = node.nickname ? node.nickname : node.first_name + ' ' + node.last_name;
        props.radius = 3 + Math.ceil(Math.sqrt(node.age * 2));

        return props
    };

    edgeDisplayProps = (edge) => {
        return {
            dashing: edge.newest_status.date_end ? [2, 2] : [],
            width: edge.newest_status.date_end ? 1 : Math.ceil(Math.log(Math.sqrt(edge.newest_status.duration / 10))),
            color: enums.relationshipColors[edge.newest_status.status]
        }
    };

    calculateDisplayProps = () => {
        this.graph.nodes.forEach((node) => {
            node.displayProps = this.nodeDisplayProps(node)
        });
        this.graph.edges.forEach((edge) => {
            edge.displayProps = this.edgeDisplayProps(edge)
        });
    };

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
        if (node.displayProps.selected) {
            this.context.strokeStyle = '#fff'
        }
        this.context.stroke();
        if (node.displayProps.pie.length > 0) {
            node.displayProps.pie.forEach((section) => {
                this.context.beginPath();
                this.context.moveTo(node.x, node.y);
                this.context.arc(node.x, node.y, node.displayProps.radius, section.angleEnd, section.angleStart, true);
                this.context.closePath();
                this.context.fillStyle = section.color;
                this.context.fill();
            });
        } else {
            this.context.fillStyle = '#666';
            this.context.fill();
        }
        this.context.font = "normal normal bold 12px sans-serif";
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
        this.context.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.context.translate(transform.x, transform.y);
        this.context.scale(transform.k, transform.k);

        this.graph.edges.forEach((edge) => {
            this.renderEdge(edge);
        });
        this.graph.nodes.forEach((node) => {
            this.renderNode(node);
        });

        this.context.restore();
    }
}


class GraphSimulation {
    constructor(graph, canvas) {
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
        for (i = 0; i < this.graph.nodes.length; ++i) {
            const node = this.graph.nodes[i];
            dx = x - node.x;
            dy = y - node.y;
            if (dx * dx + dy * dy < node.displayProps.radius * node.displayProps.radius) {
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

function dateToString(date, now_when_null = true) {
    const dateOpt = {year: 'numeric', month: 'numeric', day: 'numeric'};
    return date ? date.toLocaleString('sk-SK', dateOpt) : (now_when_null ? 'now' : '')
}

function prepend(arr, value) {
    let newArray = arr.slice();
    newArray.unshift(value);
    return newArray
}

function timeDelta(later, sooner) {
    const diff = (later ? later : new Date()) - (sooner ? sooner : new Date());
    const milliseconds_in_days = 1000 * 60 * 60 * 24;
    return {
        hours: diff / (milliseconds_in_days / 24),
        days: diff / milliseconds_in_days,
        months: diff / (milliseconds_in_days * 30),
        years: diff / (milliseconds_in_days * 365)
    }
}

function stringsToDates(obj, fields) {
    fields.forEach((field) => {
        obj[field] = typeof obj[field] == 'string' ? new Date(obj[field]) : obj[field]
    });
    return obj
}

enums['seminarColors'] = {
    KSP: '#818f3d',
    KMS: '#4a6fd8',
    FKS: '#e39f3c',
};

enums['relationshipColors'] = {
    [enums.StatusChoices.bloodRelative]: '#008080',
    [enums.StatusChoices.sibling]: '#008700',
    [enums.StatusChoices.parentChild]: '#8080ff',
    [enums.StatusChoices.married]: '#b70000',
    [enums.StatusChoices.engaged]: '#ffc000',
    [enums.StatusChoices.dating]: '#ffffff',
    [enums.StatusChoices.rumour]: '#ff00ff',
};