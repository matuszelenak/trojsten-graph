import {Graph, GraphEdge, GraphNode} from "./Graph";
import {RelationshipStatus} from "./DataTypes";
import {GroupCategory, RelationshipStatusType} from "./Enums";
import {RelationshipStatusTypeFilter} from "./components/RelationshipStatusTypeFilter";

export interface NodeFilter {
    isIncluded: (node: GraphNode) => boolean
}

export interface EdgeFilter {
    isiIncluded: (edge: GraphEdge) => boolean
}

export class SeminarFilter implements NodeFilter {
    private seminarName: string;
    private isActive: boolean;
    constructor(seminarName: string, isActive: boolean) {
        this.seminarName = seminarName
        this.isActive = isActive
    }

    isIncluded(node: GraphNode): boolean {
        return node.person.memberships.filter((membership) => {
            return membership.groupName == this.seminarName
        }).length > 0
    }
}

export class GraphView {
    public nodes: Array<GraphNode>
    public edges: Array<GraphEdge>

    constructor(nodes: Array<GraphNode>, edges: Array<GraphEdge>) {
        this.nodes = nodes
        this.edges = edges
    }
}
