import {Person, Relationship} from "./DataTypes";
import {SimulationLinkDatum, SimulationNodeDatum} from "d3";
import {getEdgeDisplayProps, getNodeDisplayProps} from "./DisplayUtils";
import {normalizeString} from "./Utils";

export type EdgeDisplayProps = {
    color: string,
    width: number,
    dashing: Array<number>
}

export type NodeDisplayProps = {
    radius: number,
    isHighlighted: boolean,
    seminarPie: Array<{
        angleStart: number,
        angleEnd: number,
        color: string
    }>
}

export type GraphNode = SimulationNodeDatum & {
    id: number,
    person: Person,
    displayX: number,
    displayY: number,
    displayProps: NodeDisplayProps,
    searchAttributes: {
        normalizedFirstName: string,
        normalizedLastName: string,
        normalizedNickname: string,
        normalizedMaidenName: string
    }
}

export type GraphEdge = SimulationLinkDatum<GraphNode> & {
    id: number,
    sourceId: number,
    targetId: number,
    relationship: Relationship,
    displayProps: EdgeDisplayProps
}

export class Graph {
    public nodes: Array<GraphNode>
    public edges: Array<GraphEdge>

    constructor(people: Array<Person>, relationships: Array<Relationship>) {
        this.nodes = people.map((person) => {
            return {
                id: person.id,
                person: person,
                displayX: 0,
                displayY: 0,
                displayProps: getNodeDisplayProps(person),
                searchAttributes: {
                    normalizedFirstName: normalizeString(person.firstName) ?? '',
                    normalizedLastName: normalizeString(person.lastName) ?? '',
                    normalizedNickname: normalizeString(person.nickname) ?? '',
                    normalizedMaidenName: normalizeString(person.maidenName) ?? ''
                }
            }
        })
        this.edges = relationships.map((relationship) => {
            return {
                id: relationship.id,
                source: relationship.source,
                target: relationship.target,
                sourceId: relationship.source,
                targetId: relationship.target,
                relationship: relationship,
                displayProps: getEdgeDisplayProps(relationship)
            }
        })
    }

    getEdgeNodes = (source: number, target: number) => {
        return [
            this.nodes.find((node) => {
                return node.id == source
            }),
            this.nodes.find((node) => {
                return node.id == target
            })
        ]
    }
}