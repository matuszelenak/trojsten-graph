var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var PersonDetail = function (_React$Component) {
    _inherits(PersonDetail, _React$Component);

    function PersonDetail() {
        _classCallCheck(this, PersonDetail);

        return _possibleConstructorReturn(this, (PersonDetail.__proto__ || Object.getPrototypeOf(PersonDetail)).apply(this, arguments));
    }

    _createClass(PersonDetail, [{
        key: 'render',
        value: function render() {
            return React.createElement(
                'div',
                { className: 'info-sidebar' },
                React.createElement(
                    'div',
                    { className: 'row' },
                    React.createElement(
                        'h2',
                        null,
                        this.props.person.nick
                    )
                )
            );
        }
    }]);

    return PersonDetail;
}(React.Component);

var RelationshipDetail = function (_React$Component2) {
    _inherits(RelationshipDetail, _React$Component2);

    function RelationshipDetail() {
        _classCallCheck(this, RelationshipDetail);

        return _possibleConstructorReturn(this, (RelationshipDetail.__proto__ || Object.getPrototypeOf(RelationshipDetail)).apply(this, arguments));
    }

    return RelationshipDetail;
}(React.Component);

var TrojstenGraph = function (_React$Component3) {
    _inherits(TrojstenGraph, _React$Component3);

    function TrojstenGraph(props) {
        _classCallCheck(this, TrojstenGraph);

        var _this3 = _possibleConstructorReturn(this, (TrojstenGraph.__proto__ || Object.getPrototypeOf(TrojstenGraph)).call(this, props));

        _this3.canvasClick = function (e) {
            _this3.setState({
                selectedPerson: _this3.simulation.nodeOnMousePosition(e.clientX, e.clientY)
            });
        };

        _this3.canvasMouseMove = function (e) {
            var node = _this3.simulation.nodeOnMousePosition(e.clientX, e.clientY);
            if (node) {
                _this3.canvas.style.cursor = 'pointer';
            } else {
                _this3.canvas.style.cursor = 'default';
            }
        };

        _this3.state = {
            selectedPerson: null
        };
        return _this3;
    }

    _createClass(TrojstenGraph, [{
        key: 'componentDidMount',
        value: function componentDidMount() {
            this.canvas = this.refs.canvas;
            var preprocessor = new GraphDataPreprocessor(this.props.graph, this.props.enums);
            this.renderer = new GraphRenderer(this.props.graph, this.canvas);
            this.simulation = new GraphSimulation(this.props.graph, this.canvas);
            this.simulation.render = this.renderer.renderGraph;
        }
    }, {
        key: 'render',
        value: function render() {
            return React.createElement(
                'div',
                null,
                React.createElement('canvas', {
                    ref: 'canvas', width: window.innerWidth, height: window.innerHeight,
                    onClick: this.canvasClick, onMouseMove: this.canvasMouseMove }),
                this.state.selectedPerson && React.createElement(PersonDetail, { person: this.state.selectedPerson })
            );
        }
    }]);

    return TrojstenGraph;
}(React.Component);

function initializeGraph(graph, enums) {
    ReactDOM.render(React.createElement(TrojstenGraph, { graph: graph, enums: enums }), document.getElementById('container'));
}