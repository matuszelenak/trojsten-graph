import React from "react";
import {Form} from "react-bootstrap";
import {RelationshipStatusType} from "../Enums";

type RelationshipStatusTypeFilterProps = {
    relationshipStatusType: RelationshipStatusType,
    label: string
}

type RelationshipStatusTypeFilterState = {
    current: boolean,
    past: boolean
}

export class RelationshipStatusTypeFilter extends React.Component<RelationshipStatusTypeFilterProps, RelationshipStatusTypeFilterState> {
    render() {
        return (
            <tr>
                <td>{this.props.label}</td>
                <td><Form.Check
                    type="switch"
                    onChange={(e) => {
                        this.setState({current: e.currentTarget.checked})
                    }}
                /></td>
                <td><Form.Check
                    type="switch"
                    onChange={(e) => {
                        this.setState({past: e.currentTarget.checked})
                    }}
                /></td>
            </tr>
        )
    }
}