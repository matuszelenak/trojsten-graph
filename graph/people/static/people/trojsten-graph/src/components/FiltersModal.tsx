import {Container, Form, Modal, ModalProps, Table} from "react-bootstrap";
import {RelationshipStatusType} from "../Enums";
import Button from "react-bootstrap/Button";
import React from "react";
import {GraphView} from "../GraphView";
import {Graph} from "../Graph";
import {GraphSimulation} from "../GraphSimulation";
import {VariableDate} from "../Utils";
import {first, last} from "lodash";
import {RelationshipStatus} from "../DataTypes";

type FiltersModalProps = ModalProps & {
    graph: Graph,
    simulation: GraphSimulation | null
}

type RelationshipStatusTypeFilter = {
    label: string
    statusType: RelationshipStatusType
    showCurrent: boolean
    showPast: boolean
}

type FiltersModalState = {
    date: VariableDate
    relationshipStatusFilters: {
        [key: number]: RelationshipStatusTypeFilter
    }
}

export class FiltersModal extends React.Component<FiltersModalProps, FiltersModalState> {
    constructor(props: FiltersModalProps) {
        super(props);
        this.state = {
            date: {
                day: 20,
                month: 10,
                year: 2021
            },
            relationshipStatusFilters: {
                [RelationshipStatusType.RUMOUR]: {label: "Rumour", showCurrent: true, showPast: true, statusType: RelationshipStatusType.RUMOUR},
                [RelationshipStatusType.DATING]: {label: "Dating", showCurrent: true, showPast: true, statusType: RelationshipStatusType.DATING},
                [RelationshipStatusType.ENGAGED]: {label: "Engaged", showCurrent: true, showPast: true, statusType: RelationshipStatusType.ENGAGED},
                [RelationshipStatusType.MARRIED]: {label: "Married", showCurrent: true, showPast: true, statusType: RelationshipStatusType.MARRIED},
                [RelationshipStatusType.BLOOD_RELATIVE]: {label: "Blood relatives", showCurrent: true, showPast: true, statusType: RelationshipStatusType.BLOOD_RELATIVE},
                [RelationshipStatusType.SIBLING]: {label: "Siblings", showCurrent: true, showPast: true, statusType: RelationshipStatusType.SIBLING},
                [RelationshipStatusType.PARENT_CHILD]: {label: "Parent-child", showCurrent: true, showPast: true, statusType: RelationshipStatusType.PARENT_CHILD}
            }
        };
    }

    onFilterUpdate = () => {
        const filteredEdges = this.props.graph.edges.filter((edge) => {
            // @ts-ignore
            const currentStatus: RelationshipStatus = first(edge.relationship.statuses)
            return Object.entries(this.state.relationshipStatusFilters).reduce((acc: boolean, [_, elem]) => {
                const currentCheck: boolean = (elem.showCurrent && currentStatus.dateEnd == null)
                const pastCheck: boolean = (elem.showPast && currentStatus.dateEnd !== null)
                return acc || (currentStatus.status == elem.statusType && (currentCheck || pastCheck))
            }, false)
        })

        if (this.props.simulation !== null) {
            this.props.simulation.setData(new GraphView(this.props.graph.nodes, filteredEdges))
        }
    }

    render() {
        const {graphView, onUpdateCallback, ...rest} = this.props
        return (
            <Modal{...rest} aria-labelledby="contained-modal-title-vcenter" centered>
                <Modal.Header closeButton ></Modal.Header>
                <Modal.Body>
                    <Container>

                        <h2>Relationships</h2>
                        <Table>
                            <thead>
                            <tr>
                                <td>Type</td>
                                <td>Current</td>
                                <td>Past</td>
                            </tr>
                            </thead>
                            <tbody>
                            {
                                Object.values(this.state.relationshipStatusFilters).map((filter) => {
                                        return (
                                            <tr>
                                                <td>{filter.label}</td>
                                                <td><Form.Check
                                                    key={filter.statusType + "current"}
                                                    type="switch"
                                                    checked={this.state.relationshipStatusFilters[filter.statusType].showCurrent}
                                                    onChange={(e) => {
                                                        const checked = e.target.checked
                                                        this.setState((state: FiltersModalState) => {
                                                            return {
                                                                ...state,
                                                                relationshipStatusFilters: {
                                                                    ...state.relationshipStatusFilters,
                                                                    [filter.statusType]: {
                                                                        ...state.relationshipStatusFilters[filter.statusType],
                                                                        showCurrent: checked
                                                                    }
                                                                }
                                                            }
                                                        }, this.onFilterUpdate)
                                                    }}
                                                /></td>
                                                <td><Form.Check
                                                    key={filter.statusType + "past"}
                                                    type="switch"
                                                    checked={this.state.relationshipStatusFilters[filter.statusType].showPast}
                                                    onChange={(e) => {
                                                        const checked = e.target.checked
                                                        this.setState((state: FiltersModalState) => {
                                                            return {
                                                                ...state,
                                                                relationshipStatusFilters: {
                                                                    ...state.relationshipStatusFilters,
                                                                    [filter.statusType]: {
                                                                        ...state.relationshipStatusFilters[filter.statusType],
                                                                        showPast: checked
                                                                    }
                                                                }
                                                            }
                                                        }, this.onFilterUpdate)
                                                    }}
                                                /></td>
                                            </tr>
                                        )
                                    }
                                )
                            }
                            </tbody>
                        </Table>
                    </Container>
                </Modal.Body>
                <Modal.Footer>
                    <Button onClick={rest.onHide}>Close</Button>
                </Modal.Footer>
            </Modal>
        );
    }
}