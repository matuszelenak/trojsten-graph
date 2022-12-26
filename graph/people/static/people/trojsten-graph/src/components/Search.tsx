import React, {createRef} from "react";
import Fuse from "fuse.js";
import {GraphNode} from "../Graph";
import {GraphSimulation} from "../GraphSimulation";
import {normalizeString} from "../Utils";

type SearchProps = {
    simulation: GraphSimulation | null,
}

export class SearchInput extends React.Component<SearchProps, any> {
    private readonly inputRef: React.RefObject<HTMLInputElement>;
    constructor(props: SearchProps) {
        super(props);

        this.inputRef = createRef()
    }

    search = (value: string): Array<GraphNode> => {
        if (this.props.simulation !== null) {
            return new Fuse<GraphNode>(
                this.props.simulation.graphView.nodes,
                {
                    isCaseSensitive: false,
                    distance: 100,
                    keys: [
                        'searchAttributes.normalizedFirstName',
                        'searchAttributes.normalizedLastName',
                        'searchAttributes.normalizedNickname',
                        'searchAttributes.normalizedMaidenName'
                    ],
                    location: 0,
                    minMatchCharLength: 1,
                    shouldSort: true,
                    threshold: 0.1
                }
                ).search(normalizeString(value) ?? '').map(it => it.item)
        }
        return []
    }

    onKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if( e.key === 'Enter' ) {
            const searchResults = this.search(this.inputRef.current?.value ?? '')
            if (searchResults.length == 1) {
                this.props.simulation?.focusViewOnNode(searchResults[0])
            }
        }
    }

    render() {
        return (
            <div className="search-field">
                <input ref={this.inputRef} type="text" placeholder="Search..." onKeyPress={this.onKeyPress}/>
            </div>
        )
    }
}