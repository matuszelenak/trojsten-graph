class PersonDetail extends React.Component {
    render() {
        return (
            <div className='info-sidebar'>
                <div className="row">
                    <h2>{this.props.person.nickname}</h2>
                </div>
            </div>
        )
    }
}

class RelationshipDetail extends React.Component {

}


class TrojstenGraph extends React.Component {
    constructor(props){
        super(props);
        this.state = {
            selectedPerson: null
        }
    }

    componentDidMount() {
        this.canvas = this.refs.canvas;
        const preprocessor = new GraphDataPreprocessor(this.props.graph, this.props.enums);
        this.renderer = new GraphRenderer(this.props.graph, this.canvas);
        this.simulation = new GraphSimulation(this.props.graph, this.canvas);
        this.simulation.render = this.renderer.renderGraph
    }

    canvasClick = (e) => {
        this.setState({
            selectedPerson: this.simulation.nodeOnMousePosition(e.clientX, e.clientY)
        });
    };

    canvasMouseMove = (e) => {
        const node = this.simulation.nodeOnMousePosition(e.clientX, e.clientY);
        if (node) {
            this.canvas.style.cursor = 'pointer'
        } else {
            this.canvas.style.cursor = 'default'
        }
    };

    render() {
        return (
            <div>
                <canvas
                    ref="canvas" width={window.innerWidth} height={window.innerHeight}
                    onClick={this.canvasClick} onMouseMove={this.canvasMouseMove}>
                </canvas>
                { this.state.selectedPerson && <PersonDetail person={this.state.selectedPerson}/>}
            </div>
        )
    }
}

function initializeGraph(graph, enums){
    ReactDOM.render(
        <TrojstenGraph graph={graph} enums={enums}/>,
        document.getElementById('container')
    );
}