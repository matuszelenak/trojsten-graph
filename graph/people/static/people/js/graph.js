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
            var person = this.props.person;
            return React.createElement(
                'div',
                { className: 'info-sidebar' },
                React.createElement(
                    'div',
                    { className: 'row' },
                    React.createElement(
                        'h2',
                        null,
                        person.first_name,
                        ' ',
                        person.nickname ? '"' + person.nickname + '"' : '',
                        ' ',
                        person.last_name
                    ),
                    React.createElement(
                        'p',
                        null,
                        'Born on ',
                        dateToString(new Date(person.birth_date))
                    )
                ),
                person.memberships.length > 0 && React.createElement(
                    'div',
                    null,
                    React.createElement(
                        'h3',
                        null,
                        'Member of groups'
                    ),
                    React.createElement(
                        'ul',
                        null,
                        person.memberships.map(function (membership) {
                            return React.createElement(
                                'li',
                                { key: membership.group_name },
                                membership.group_name,
                                ': From ',
                                dateToString(membership.date_started),
                                ' to ',
                                dateToString(membership.date_ended)
                            );
                        })
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

    _createClass(RelationshipDetail, [{
        key: 'render',
        value: function render() {
            return React.createElement(
                'div',
                { className: 'info-sidebar' },
                React.createElement(
                    'h2',
                    null,
                    this.props.firstPerson.displayProps.label,
                    ' & ',
                    this.props.secondPerson.displayProps.label
                ),
                React.createElement(
                    'h3',
                    null,
                    'Relationship history'
                ),
                React.createElement(
                    'ul',
                    null,
                    this.props.relationship.statuses.map(function (status, i) {
                        return React.createElement(
                            'li',
                            { key: i },
                            labels.StatusChoices[status.status],
                            ': From ',
                            dateToString(status.date_start),
                            ' to ',
                            dateToString(status.date_end)
                        );
                    })
                )
            );
        }
    }]);

    return RelationshipDetail;
}(React.Component);

var TrojstenGraph = function (_React$Component3) {
    _inherits(TrojstenGraph, _React$Component3);

    function TrojstenGraph(props) {
        _classCallCheck(this, TrojstenGraph);

        var _this3 = _possibleConstructorReturn(this, (TrojstenGraph.__proto__ || Object.getPrototypeOf(TrojstenGraph)).call(this, props));

        _this3.getRelationship = function (firstPerson, secondPerson) {
            return _this3.props.graph.edges.find(function (edge) {
                if (edge.source === firstPerson && edge.target === secondPerson || edge.source === secondPerson && edge.target === firstPerson) {
                    return true;
                }
            });
        };

        _this3.updateDimensions = function () {
            _this3.setState({ width: window.innerWidth, height: window.innerHeight });
            _this3.simulation.update();
        };

        _this3.canvasClick = function (e) {
            var clickedNode = _this3.simulation.nodeOnMousePosition(e.clientX, e.clientY);
            var selectedNodes = clickedNode ? prepend(_this3.state.selectedPeople, clickedNode).slice(0, 2) : [];
            _this3.setState({
                selectedPeople: selectedNodes
            });
            _this3.props.graph.nodes.forEach(function (node) {
                node.displayProps.selected = selectedNodes.includes(node);
            });
            _this3.simulation.update();
        };

        _this3.search = function (e) {
            _this3.props.graph.nodes.forEach(function (node) {});
        };

        _this3.canvasMouseMove = function (e) {
            _this3.canvas.style.cursor = _this3.simulation.nodeOnMousePosition(e.clientX, e.clientY) ? 'pointer' : 'default';
        };

        _this3.getSidebar = function () {
            var firstPerson = _this3.state.selectedPeople[0],
                secondPerson = _this3.state.selectedPeople[1],
                relationship = void 0;
            if (firstPerson) {
                if (secondPerson && (relationship = _this3.getRelationship(firstPerson, secondPerson))) {
                    return React.createElement(RelationshipDetail, {
                        firstPerson: firstPerson,
                        secondPerson: secondPerson,
                        relationship: relationship
                    });
                }
                return React.createElement(PersonDetail, { person: firstPerson });
            }
        };

        _this3.state = {
            selectedPeople: [],
            width: window.innerWidth,
            height: window.innerHeight
        };

        var options = {
            shouldSort: true,
            threshold: 0.1,
            location: 0,
            distance: 100,
            maxPatternLength: 32,
            minMatchCharLength: 1,
            keys: ['first_name', 'last_name', 'nickname', 'maiden_name']
        };
        _this3.fuse = new Fuse(props.graph.nodes, options);
        return _this3;
    }

    _createClass(TrojstenGraph, [{
        key: 'componentDidMount',
        value: function componentDidMount() {
            window.addEventListener('resize', this.updateDimensions);
            this.canvas = this.refs.canvas;
            this.searchInput = this.refs.search_query;
            preprocessGraph(this.props.graph);
            this.renderer = new GraphRenderer(this.props.graph, this.canvas);
            this.simulation = new GraphSimulation(this.props.graph, this.canvas);
            this.simulation.render = this.renderer.renderGraph;
        }
    }, {
        key: 'componentWillUnmount',
        value: function componentWillUnmount() {
            window.removeEventListener('resize', this.updateDimensions);
        }
    }, {
        key: 'render',
        value: function render() {
            var searchBar = React.createElement(
                'div',
                { className: 'search-bar' },
                React.createElement('input', { ref: 'search_query', type: 'text' }),
                React.createElement(
                    'button',
                    { onClick: this.search },
                    'Search'
                )
            );
            return React.createElement(
                'div',
                null,
                React.createElement('canvas', { tabIndex: '1', ref: 'canvas', width: this.state.width, height: this.state.height,
                    onClick: this.canvasClick, onMouseMove: this.canvasMouseMove }),
                this.getSidebar()
            );
        }
    }]);

    return TrojstenGraph;
}(React.Component);

function initializeGraph(graph) {
    ReactDOM.render(React.createElement(TrojstenGraph, { graph: graph }), document.getElementById('container'));
}