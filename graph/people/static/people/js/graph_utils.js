import * as d3 from "d3";
import {enums} from "./graph_enums";

function preprocessGraph(graph) {
    graph.nodes.forEach((node) => {
        stringsToDates(node, ['birth_date', 'death_date']);
        node.memberships.forEach((membership) => {
            stringsToDates(membership, ['date_started', 'date_ended']);
        });
    });
    graph.edges.forEach((edge, index) => {
        edge.id = index;
        edge.sourceId = edge.source;
        edge.targetId = edge.target;
        edge.statuses.forEach((status) => {
            stringsToDates(status, ['date_start', 'date_end']);
        });
    });
}

function computeExtraGraphData(graph, currentTime) {
    graph.nodes.forEach((node) => {
        node.memberships.forEach((membership) => {
            membership.duration = timeDelta(
                membership.date_ended !== null ? Math.min(membership.date_ended, currentTime) : null,
                membership.date_started
            ).days
        });
        node.age = timeDelta(
            node.death_date !== null ? Math.min(node.death_date, currentTime) : null,
            node.birth_date
        ).years;
        node.searchAttributes = {
            first_name: normalizeString(node.first_name),
            last_name: normalizeString(node.last_name),
            nickname: node.nickname ? normalizeString(node.nickname) : '',
            maiden_name: node.maiden_name ? normalizeString(node.maiden_name) : ''
        };
        node.isHighlighted = false;
    });
    graph.edges.forEach((edge) => {
        edge.statuses.forEach((status) => {
            status.duration = timeDelta(
                status.date_end !== null ? Math.min(status.date_end, currentTime) : null,
                status.date_start
            ).days
        });
        let current = null;
        const statuses = edge.statuses
            .sort((a, b) => a.date_start < b.date_start ? 1 : -1)
            .filter((status) => status.date_start < currentTime);
        if (statuses.length > 0) {
            statuses[0].isEnded = statuses[0].date_end === null ? false : (statuses[0].date_end < currentTime);
            current = statuses[0]
        }
        edge.currentStatus = current
    })
}

class GraphFilter {
    constructor(graph) {
        this.original = graph;
        this.filters = {
            isKSP: {
                label: 'KSP',
                value: true
            },
            isKMS: {
                label: 'KMS',
                value: true
            },
            isFKS: {
                label: 'FKS',
                value: true
            },
            notTrojsten: {
                label: 'Non-Trojsten',
                value: true
            },
            isIsolated: {
                label: 'Isolated',
                value: true
            },
            isCurrentSerious: {
                label: 'Current serious',
                value: true
            },
            isOldSerious: {
                label: 'Old serious',
                value: true
            },
            isBloodBound: {
                label: 'Blood bound',
                value: true
            },
            isCurrentRumour: {
                label: 'Current rumours',
                value: true
            },
            isOldRumour: {
                label: 'Old rumours',
                value: true
            },
        };
        this.graph = {
            nodes: [...this.original.nodes],
            edges: [...this.original.edges]
        };
        this.onFilterCallback = () => {
        };
        this.onFilterUpdate = (callback) => {
            this.onFilterCallback = callback
        };
    }

    updateFilterValue = (key, value) => {
        this.filters[key].value = value;
        this.filterGraph();
    };

    setCurrentTime = (time) => {
        this.currentTime = time;
        computeExtraGraphData(this.original, this.currentTime);
        this.filterGraph();
    };

    getFilterOptions = (...args) => {
        return Object.entries(this.filters).filter(([name, params]) => {
            return args.length > 0 ? args.includes(name) : true
        }).map(([name, params]) => {
            params.name = name;
            return params
        })
    };

    trojstenFilter = (person) => {
        const memberships = seminarMemberships(person);
        if (memberships.length === 0 && this.filters.notTrojsten.value) {
            return true
        }
        const selectedSeminars = new Set(
            Object.keys(this.filters).filter(
                key => ['isKMS', 'isKSP', 'isFKS'].includes(key) && this.filters[key].value
            ).map(key => this.filters[key].label)
        );
        return seminarMemberships(person).filter(seminar => selectedSeminars.has(seminar)).length > 0;
    };

    isIsolated = (person) => {
        return this.filters.isIsolated.value || this.graph.edges.filter(edge => edge.sourceId === person.id || edge.targetId === person.id).length > 0
    }

    relationshipFilter = (relationship, types, current, old) => {
        if (relationship.currentStatus.isEnded && !old)
            return false;
        if (!relationship.currentStatus.isEnded && !current)
            return false;
        return types.includes(relationship.currentStatus.status)
    };

    isRumour = (edge) => {
        return this.relationshipFilter(
            edge,
            [enums.StatusChoices.rumour],
            this.filters.isCurrentRumour.value,
            this.filters.isOldRumour.value
        )
    };

    isSerious = (edge) => {
        return this.relationshipFilter(
            edge,
            [enums.StatusChoices.dating, enums.StatusChoices.engaged, enums.StatusChoices.married],
            this.filters.isCurrentSerious.value,
            this.filters.isOldSerious.value
        )
    };

    isBloodBound = (edge) => {
        return this.filters.isBloodBound.value === true && this.relationshipFilter(
            edge,
            [enums.StatusChoices.bloodRelative, enums.StatusChoices.parentChild, enums.StatusChoices.sibling],
            true,
            true
        )
    };

    composeFunctions = (...functions) => {
        return functions.reduce((acc, f) => {
            return (x) => f(x) || acc(x)
        }, () => false);
    };

    filteredNodeIds = () => {
        return new Set(this.original.nodes
            .filter(this.composeFunctions(this.trojstenFilter))
            .filter(this.isIsolated)
            .filter((person) => person.birth_date < this.currentTime)
            .map((person) => person.id))
    };

    filteredEdgeIds = () => {
        return new Set(this.original.edges
            .filter((relationship) => relationship.currentStatus !== null)
            .filter(this.composeFunctions(this.isSerious, this.isBloodBound, this.isRumour))
            .map((edge) => edge.id)
        )
    };

    filterGraph = () => {
        const nodeIds = [...this.filteredNodeIds()];
        this.graph.nodes = this.original.nodes.filter((node) => nodeIds.includes(node.id));

        const edgeIds = [...this.filteredEdgeIds()];
        this.graph.edges = this.original.edges.filter((edge) => edgeIds.includes(edge.id)).filter((edge) => {
            return nodeIds.includes(edge.sourceId) && nodeIds.includes(edge.targetId)
        });
        this.onFilterCallback(this.graph);
    }
}

class GraphRenderer {
    constructor(canvas) {
        this.graph = {nodes: [], edges: []};
        this.canvas = canvas;
        this.context = this.canvas.getContext('2d');

        this.pulseRadius = 0;
        this.pulseVelocity = 20;
    }

    pulseSearchResults = () => {
        if (this.pulseVelocity < 0.1) {
            this.resetPulse();
        }
        this.pulseRadius = this.pulseRadius + this.pulseVelocity;
        this.pulseVelocity *= 0.9;
    };

    resetPulse = () => {
        this.pulseVelocity = 20;
        this.pulseRadius = 0;
    };

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

        if (node.isHighlighted) {
            props.label = node.first_name + ' ' + node.last_name;
        } else props.label = node.nickname ? node.nickname : node.first_name + ' ' + node.last_name;
        props.radius = 3 + Math.ceil(Math.sqrt(node.age * 2));

        return props
    };

    edgeDisplayProps = (edge) => {
        return {
            dashing: edge.currentStatus.isEnded ? [2, 2] : [],
            width: edge.currentStatus.isEnded ? 1 : Math.ceil(Math.log(Math.sqrt(edge.currentStatus.duration / 10))),
            color: enums.relationshipColors[edge.currentStatus.status]
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

    setData = (graph) => {
        this.graph = graph;
        this.calculateDisplayProps()
    };

    highlightNode = (target) => {
        this.graph.nodes.forEach((node) => {
            node.isHighlighted = node === target
        });
        this.graph.nodes.forEach((node) => {
            node.displayProps = this.nodeDisplayProps(node)
        });
    };

    renderEdge = (edge) => {
        this.context.beginPath();
        this.context.lineWidth = edge.displayProps.width;
        this.context.strokeStyle = edge.displayProps.color;
        this.context.setLineDash(edge.displayProps.dashing);
        this.context.moveTo(edge.source.displayX, edge.source.displayY);
        this.context.lineTo(edge.target.displayX, edge.target.displayY);
        this.context.stroke();
    };

    renderNode = (node) => {
        if (node.displayProps.selected) {
            this.context.beginPath();
            this.context.lineWidth = 2;
            this.context.moveTo(node.displayX, node.displayY);
            this.context.arc(node.displayX, node.displayY, node.displayProps.radius, 0, 2 * Math.PI, true);
            this.context.strokeStyle = '#fff';
            this.context.stroke();
        }

        if (node.displayProps.pie.length > 0) {
            node.displayProps.pie.forEach((section) => {
                this.context.beginPath();
                this.context.moveTo(node.displayX, node.displayY);
                this.context.arc(node.displayX, node.displayY, node.displayProps.radius, section.angleEnd, section.angleStart, true);
                this.context.fillStyle = section.color;
                this.context.fill();
            });
        } else {
            this.context.beginPath();
            this.context.arc(node.displayX, node.displayY, node.displayProps.radius, 0, 2 * Math.PI, true);
            this.context.fillStyle = '#666';
            this.context.fill();
        }

        this.context.fillStyle = "#FFF";
        this.context.fillText(
            node.displayProps.label,
            node.displayX - this.context.measureText(node.displayProps.label).width / 2,
            node.displayY - node.displayProps.radius - 2
        );

        if (node.isSearchResult) {
            this.context.beginPath();
            this.context.arc(node.displayX, node.displayY, this.pulseRadius, 0, 2 * Math.PI, false);
            this.context.strokeStyle = '#ff000055';
            this.context.fillStyle = '#ff000055';
            this.context.fill();
            this.context.stroke();
        }


        if (node.death_date) {
            this.context.save();

            this.context.beginPath();
            this.context.arc(node.displayX, node.displayY, node.displayProps.radius, 0, 2 * Math.PI);
            this.context.closePath();
            this.context.clip();
            this.context.beginPath();
            this.context.strokeStyle = '#000000';
            this.context.lineWidth = 3;
            this.context.moveTo(node.displayX - node.displayProps.radius * 0.75, node.displayY + node.displayProps.radius * 1.5);
            this.context.lineTo(node.displayX + node.displayProps.radius * 1.5, node.displayY - node.displayProps.radius * 0.75);
            this.context.closePath();
            this.context.stroke();

            this.context.restore();
        }
    };

    renderGraph = (transform) => {
        this.context.save();
        this.context.clearRect(0, 0, this.canvas.width, this.canvas.height);
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
    constructor(canvas) {
        this.canvas = canvas;
        this.simulation = d3.forceSimulation()
            .force("center", d3.forceCenter(this.canvas.width / 2, this.canvas.height / 2))
            .force("collide", d3.forceCollide())
            .force("x", d3.forceX(this.canvas.width / 2).strength(0.04))
            .force("y", d3.forceY(this.canvas.height / 2).strength(0.04))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("link", d3.forceLink().strength(0.2).id((node) => node.id));

        d3.select(this.canvas)
            .call(d3.drag().subject(this.dragsubject)
                .on("start", this.dragstarted)
                .on("drag", this.dragged)
                .on("end", this.dragended))
            .call(d3.zoom().scaleExtent([1 / 10, 8]).on("zoom", this.zoomed));

        this.nodes = [];
        this.edges = [];

        this.render = () => {
        };
        this.transform = d3.zoomIdentity;
        this.simulation.on("tick", this.update);
    }

    setData = (graph) => {
        this.nodes = graph.nodes;
        this.edges = graph.edges;
        this.simulation.nodes(this.nodes);
        this.simulation.force("link").links(this.edges);
        this.simulation.alphaTarget(0.3).alphaDecay(0.05).restart();
    };

    update = () => {
        this.nodes.forEach((node) => {
            node.displayX = ~~node.x;
            node.displayY = ~~node.y;
        });
        this.render(this.transform);
    };

    nodeOnMousePosition = (mouseX, mouseY) => {
        let i, dx, dy, x = this.transform.invertX(mouseX), y = this.transform.invertY(mouseY);
        for (i = 0; i < this.nodes.length; ++i) {
            const node = this.nodes[i];
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

function seminarMemberships(person) {
    return person.memberships.filter((membership) => ['KSP', 'KMS', 'FKS'].includes(membership.group_name))
        .map((membership) => membership.group_name)
}

function normalizeString(str) {
    return str.normalize('NFKD').replace(/[\u0300-\u036F]/g, '')
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

export {preprocessGraph, GraphFilter, GraphRenderer, GraphSimulation, dateToString, prepend, normalizeString};
