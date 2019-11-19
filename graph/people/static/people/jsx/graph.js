class PersonDetail extends React.Component {
    render() {
        const person = this.props.person;
        return (
            <div className='info-sidebar'>
                <div className="row">
                    <h2>{person.first_name} {person.nickname ? '"' + person.nickname + '"' : ''} {person.last_name}</h2>
                    <p>Born on {dateToString(new Date(person.birth_date))}</p>
                </div>
                {person.memberships.length > 0 &&
                <div>
                    <h3>Member of groups</h3>
                    <ul>
                        {person.memberships.map((membership) =>
                            <li key={membership.group_name}>
                                {membership.group_name}:
                                From {dateToString(membership.date_started)} to {dateToString(membership.date_ended)}
                            </li>
                        )}
                    </ul>
                </div>
                }
            </div>
        )
    }
}

class RelationshipDetail extends React.Component {
    render() {
        return (
            <div className='info-sidebar'>
                <h2>{this.props.firstPerson.displayProps.label} & {this.props.secondPerson.displayProps.label}</h2>
                <h3>Relationship history</h3>
                <ul>
                    {this.props.relationship.statuses.map((status, i) =>
                        <li key={i}>
                            {labels.StatusChoices[status.status]}:
                            From {dateToString(status.date_start)} to {dateToString(status.date_end)}
                        </li>
                    )}
                </ul>
            </div>
        )
    }
}

class GraphFilterPanel extends React.Component {
    constructor(props) {
        super(props);
        this.filter = props.filter;
        this.state = this.filter.getFilterOptions().reduce((acc, option) => {
            acc[option.name] = option.value;
            return acc
        }, {})
    }

    handleInputChange = (event) => {
        this.setState({
            [event.target.name]: event.target.checked
        });
        this.filter.updateFilterValue(event.target.name, event.target.checked)
    };

    inputGroup = (label, optionGroup) =>
        <div key={label}>
            <h2>{label}</h2>
            <table>
                <tbody>
                {optionGroup.map((options, i) =>
                    <tr key={i}>
                        {options.map((option) =>
                            <td key={option.name}>
                                <input key={option.name} type='checkbox' checked={this.state[option.name] === true ? 'checked': ''}
                                       name={option.name} onChange={this.handleInputChange} id={option.name}
                                />
                                <label htmlFor={option.name}>{option.label}</label>
                            </td>
                        )}
                    </tr>
                )}
                </tbody>
            </table>
        </div>;

    render() {
        const peopleFilters = this.filter.getFilterOptions('isKSP', 'isKMS', 'isFKS', 'notTrojsten').map(arr => [arr]);
        const relationshipFilters = [
            this.filter.getFilterOptions('isCurrentSerious', 'isOldSerious'),
            this.filter.getFilterOptions('isCurrentRumour', 'isOldRumour'),
            this.filter.getFilterOptions('isBloodBound'),
        ];
        return <div className='graph-filter'>
            {this.inputGroup('People', peopleFilters)}
            {this.inputGroup('Relationships', relationshipFilters)}
        </div>
    }
}


class GraphTimelinePanel extends React.Component {
    constructor(props){
        super(props)
    }

    componentDidMount () {
        const slider = document.getElementById('time-setter');
        let event_dates =
            this.props.graph.edges.map((edge) => edge.statuses.map(status => [status.date_start, status.date_end])).flat(2)
        event_dates = [...new Set(event_dates)].filter(x => x !== null).sort((a, b) => a - b);

        let ranges = {};
        let min_date = event_dates[0].getTime(), max_date = event_dates[event_dates.length -1].getTime();
        if (event_dates.length > 2){
            event_dates.slice(1, -1).reduce((ranges, date) => {
                const percentage = ((date - min_date) / (max_date - min_date)) * 100;
                ranges[percentage + '%'] = date.getTime();
                return ranges
            }, ranges);
        }
        ranges['min'] = min_date;
        ranges['max'] = max_date;
        noUiSlider.create(slider, {
            start: max_date,
            snap: true,
            connect: 'lower',
            tooltips: {
                from: Number,
                to: (ts) => dateToString(new Date(+ts))
            },
            range: ranges,
        });
        const self = this;
        slider.noUiSlider.on('update', function(values, handle) {
            self.props.onChange(new Date(+values[handle]));
        });

    }

    render () {
        return (
            <div className='timeline-panel'>
                <div id='time-setter'></div>
            </div>
        )
    }
}


class TrojstenGraph extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            selectedPeople: [],
            width: window.innerWidth,
            height: window.innerHeight
        };

        this.filter = new GraphFilter(props.graph);

        const options = {
            shouldSort: true,
            threshold: 0.1,
            location: 0,
            distance: 100,
            maxPatternLength: 32,
            minMatchCharLength: 1,
            keys: [
                'first_name', 'last_name', 'nickname', 'maiden_name'
            ]
        };
        this.fuse = new Fuse(props.graph.nodes, options);
    }

    getRelationship = (firstPerson, secondPerson) => {
        return this.props.graph.edges.find((edge) =>
            (edge.source === firstPerson && edge.target === secondPerson) || (edge.source === secondPerson && edge.target === firstPerson)
        )
    };

    setData = (graph) => {
        this.simulation.setData(graph);
        this.renderer.setData(graph);
    };

    componentDidMount() {
        window.addEventListener('resize', this.updateDimensions);
        this.canvas = this.refs.canvas;
        this.searchInput = this.refs.search_query;
        this.renderer = new GraphRenderer(this.canvas);
        this.simulation = new GraphSimulation(this.canvas);
        this.simulation.render = this.renderer.renderGraph;
        this.filter.onFilterUpdate((graph) => this.setData(graph));
        this.filter.setCurrentTime(new Date())
    }

    componentWillUnmount() {
        window.removeEventListener('resize', this.updateDimensions);
    }

    updateDimensions = () => {
        this.setState({width: window.innerWidth, height: window.innerHeight});
        this.simulation.update();
    };

    canvasClick = (e) => {
        const clickedNode = this.simulation.nodeOnMousePosition(e.clientX, e.clientY);
        let selectedNodes = clickedNode ? prepend(this.state.selectedPeople, clickedNode).slice(0, 2) : [];
        this.setState({
            selectedPeople: selectedNodes
        });
        this.props.graph.nodes.forEach((node) => {
            node.displayProps.selected = selectedNodes.includes(node)
        });
        this.simulation.update();
    };

    search = (e) => {
        this.props.graph.nodes.forEach((node) => {

        });
    };

    canvasMouseMove = (e) => {
        this.canvas.style.cursor = this.simulation.nodeOnMousePosition(e.clientX, e.clientY) ? 'pointer' : 'default';
    };

    getSidebar = () => {
        let firstPerson = this.state.selectedPeople[0],
            secondPerson = this.state.selectedPeople[1],
            relationship;
        if (firstPerson) {
            if (secondPerson && (relationship = this.getRelationship(firstPerson, secondPerson))) {
                return <RelationshipDetail
                    firstPerson={firstPerson}
                    secondPerson={secondPerson}
                    relationship={relationship}
                />
            }
            return <PersonDetail person={firstPerson}/>
        }
    };

    render() {
        const searchBar = (
            <div className='search-bar'>
                <input ref="search_query" type='text'/>
                <button onClick={this.search}>Search</button>
            </div>
        );
        return (
            <div>
                <canvas tabIndex="1" ref="canvas" width={this.state.width} height={this.state.height}
                        onClick={this.canvasClick} onMouseMove={this.canvasMouseMove}>
                </canvas>
                <GraphFilterPanel filter={this.filter}/>
                <GraphTimelinePanel graph={this.props.graph} onChange={(e) => {this.filter.setCurrentTime(e)}}/>
                {this.getSidebar()}
            </div>
        )
    }
}

function initializeGraph(graph) {
    preprocessGraph(graph);
    ReactDOM.render(
        <TrojstenGraph graph={graph}/>,
        document.getElementById('container')
    );
}