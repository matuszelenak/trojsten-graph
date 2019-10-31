class GraphEventHandler {
    constructor(graph, canvas, simulation){
        this.graph = graph;
        this.canvas = canvas;
        this.simulation = simulation;

        this.canvas.addEventListener('mousemove', this.handleMouseMove.bind(this));
        this.canvas.addEventListener('click', this.handleMouseClick.bind(this));
    }

    handleMouseMove(event){
        const node = this.simulation.nodeOnMousePosition(event.clientX, event.clientY);
        if (node){
            this.canvas.style.cursor = 'pointer'
        }
        else {
            this.canvas.style.cursor = 'default'
        }
    }

    handleMouseClick(event){

    }
}