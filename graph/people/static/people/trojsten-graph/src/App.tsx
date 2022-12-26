import React, {createRef} from 'react';
import {GraphSimulation} from "./GraphSimulation";
import {Graph} from "./Graph";
import {GraphRenderer} from "./GraphRenderer";
import 'bootstrap/dist/css/bootstrap.min.css';
import Button from 'react-bootstrap/Button';
import {Container, Form, Nav, NavDropdown} from "react-bootstrap";
import Navbar from 'react-bootstrap/Navbar'
import {Filter} from "react-bootstrap-icons";
import {FiltersModal} from "./components/FiltersModal";
import {GraphView} from "./GraphView";

type GraphProps = {}

type GraphState = {
    width: number,
    height: number,
    showSearch: boolean,
    showModal: boolean,
    graph: Graph,
    simulation: GraphSimulation | null
}

class App extends React.Component<GraphProps, GraphState> {
    private readonly canvasRef: React.RefObject<HTMLCanvasElement>;

    constructor(props: GraphProps) {
        super(props);
        this.state = {
            width: window.innerWidth,
            height: window.innerHeight,
            showSearch: false,
            graph: new Graph([], []),
            simulation: null,
            showModal: false
        };
        this.canvasRef = createRef()
    }

    componentDidMount() {
        window.addEventListener('resize', () => {
            this.setState({
                width: window.innerWidth,
                height: window.innerHeight
            })
        });

        window.addEventListener('keydown', (e) => {
            if ((e.keyCode == 114) || (e.ctrlKey && e.keyCode == 70)) {
                // Block CTRL + F event
                this.setState({
                    showSearch: !this.state.showSearch
                })
                e.preventDefault();
            }
        });

        const renderer = new GraphRenderer(this.canvasRef.current as HTMLCanvasElement)
        const simulation = new GraphSimulation(this.canvasRef.current as HTMLCanvasElement, renderer.renderGraph)
        this.setState({simulation: simulation})

        Promise.all([
            fetch("/api/people/")
                .then(resp => {
                    if (!resp.ok) {
                        throw new Error("Something went wrong with fetching people")
                    }
                    return resp.json()
                })
                .catch(error => {
                    console.log(error)
                }),
            fetch("/api/relationships/")
                .then(resp => {
                    if (!resp.ok) {
                        throw new Error("Something went wrong with fetching relationships")
                    }
                    return resp.json()
                })
                .catch(error => {
                    console.log(error)
                }),
        ]).then(([people, relationships]) => {
            const graph = new Graph(people, relationships)
            this.setState({graph: graph})
            simulation.setData(new GraphView(graph.nodes, graph.edges))
        })
    }

    render() {
        return (
            <div>
                <canvas ref={this.canvasRef} width={this.state.width} height={this.state.height} tabIndex={1}
                        style={{position: "absolute", top: 0, left: 0, background: '#222'}}>

                </canvas>
                <Navbar collapseOnSelect expand="lg" bg="transparent" variant="dark">
                    <Container fluid>
                        <Navbar.Toggle aria-controls="responsive-navbar-nav"/>
                        <Navbar.Collapse id="responsive-navbar-nav">
                            <Nav className="me-auto">
                                <Button variant="outline-secondary" onClick={() => this.setState({showModal: true})} className="mx-1">
                                    <Filter></Filter>
                                    Filter
                                </Button>
                                <div className="d-flex mx-1">
                                    <Form.Control type="text"></Form.Control>
                                    <Button variant="outline-secondary" className="mx-1">
                                        Search
                                    </Button>
                                </div>
                            </Nav>
                            <Nav>
                                <NavDropdown title="Dropdown" id="collasible-nav-dropdown2">
                                    <NavDropdown.Item href="#action/3.2">Content management</NavDropdown.Item>
                                    <NavDropdown.Item href="#action/3.3">Change password</NavDropdown.Item>
                                    <NavDropdown.Divider/>
                                    <NavDropdown.Item href="/logout">Sign out</NavDropdown.Item>
                                </NavDropdown>
                            </Nav>
                        </Navbar.Collapse>
                    </Container>
                </Navbar>
                <FiltersModal show={this.state.showModal} onHide={() => this.setState({showModal: false})} simulation={this.state.simulation} graph={this.state.graph}/>
            </div>
        );
    }
}

export default App;
