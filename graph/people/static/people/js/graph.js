var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

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

var GraphFilterPanel = function (_React$Component3) {
    _inherits(GraphFilterPanel, _React$Component3);

    function GraphFilterPanel(props) {
        _classCallCheck(this, GraphFilterPanel);

        var _this3 = _possibleConstructorReturn(this, (GraphFilterPanel.__proto__ || Object.getPrototypeOf(GraphFilterPanel)).call(this, props));

        _this3.handleInputChange = function (event) {
            _this3.setState(_defineProperty({}, event.target.name, event.target.checked));
            _this3.filter.updateFilterValue(event.target.name, event.target.checked);
        };

        _this3.inputGroup = function (label, options) {
            return React.createElement(
                'div',
                { key: label },
                React.createElement(
                    'h2',
                    null,
                    label
                ),
                React.createElement(
                    'table',
                    null,
                    React.createElement(
                        'tbody',
                        null,
                        options.map(function (option) {
                            return React.createElement(
                                'tr',
                                { key: option.name },
                                React.createElement(
                                    'td',
                                    null,
                                    React.createElement(
                                        'label',
                                        null,
                                        option.label
                                    )
                                ),
                                React.createElement(
                                    'td',
                                    null,
                                    React.createElement('input', { key: option.name, type: 'checkbox', checked: _this3.state[option.name] === true ? 'checked' : '',
                                        name: option.name, onChange: _this3.handleInputChange
                                    })
                                )
                            );
                        })
                    )
                )
            );
        };

        _this3.filter = props.filter;
        _this3.state = _this3.filter.getFilterOptions().reduce(function (acc, option) {
            acc[option.name] = option.value;
            return acc;
        }, {});
        return _this3;
    }

    _createClass(GraphFilterPanel, [{
        key: 'render',
        value: function render() {
            return React.createElement(
                'div',
                { className: 'graph-filter' },
                this.inputGroup('People', this.filter.getFilterOptions('isKSP', 'isKMS', 'isFKS', 'notTrojsten')),
                this.inputGroup('Relationships', this.filter.getFilterOptions('isSerious', 'isRumour', 'isBloodBound'))
            );
        }
    }]);

    return GraphFilterPanel;
}(React.Component);

var TrojstenGraph = function (_React$Component4) {
    _inherits(TrojstenGraph, _React$Component4);

    function TrojstenGraph(props) {
        _classCallCheck(this, TrojstenGraph);

        var _this4 = _possibleConstructorReturn(this, (TrojstenGraph.__proto__ || Object.getPrototypeOf(TrojstenGraph)).call(this, props));

        _this4.getRelationship = function (firstPerson, secondPerson) {
            return _this4.props.graph.edges.find(function (edge) {
                if (edge.source === firstPerson && edge.target === secondPerson || edge.source === secondPerson && edge.target === firstPerson) {
                    return true;
                }
            });
        };

        _this4.setData = function (graph) {
            _this4.simulation.setData(graph);
            _this4.renderer.setData(graph);
        };

        _this4.updateDimensions = function () {
            _this4.setState({ width: window.innerWidth, height: window.innerHeight });
            _this4.simulation.update();
        };

        _this4.canvasClick = function (e) {
            var clickedNode = _this4.simulation.nodeOnMousePosition(e.clientX, e.clientY);
            var selectedNodes = clickedNode ? prepend(_this4.state.selectedPeople, clickedNode).slice(0, 2) : [];
            _this4.setState({
                selectedPeople: selectedNodes
            });
            _this4.props.graph.nodes.forEach(function (node) {
                node.displayProps.selected = selectedNodes.includes(node);
            });
            _this4.simulation.update();
        };

        _this4.search = function (e) {
            _this4.props.graph.nodes.forEach(function (node) {});
        };

        _this4.canvasMouseMove = function (e) {
            _this4.canvas.style.cursor = _this4.simulation.nodeOnMousePosition(e.clientX, e.clientY) ? 'pointer' : 'default';
        };

        _this4.getSidebar = function () {
            var firstPerson = _this4.state.selectedPeople[0],
                secondPerson = _this4.state.selectedPeople[1],
                relationship = void 0;
            if (firstPerson) {
                if (secondPerson && (relationship = _this4.getRelationship(firstPerson, secondPerson))) {
                    return React.createElement(RelationshipDetail, {
                        firstPerson: firstPerson,
                        secondPerson: secondPerson,
                        relationship: relationship
                    });
                }
                return React.createElement(PersonDetail, { person: firstPerson });
            }
        };

        _this4.state = {
            selectedPeople: [],
            width: window.innerWidth,
            height: window.innerHeight
        };

        preprocessGraph(props.graph);
        _this4.filter = new GraphFilter(props.graph);

        var options = {
            shouldSort: true,
            threshold: 0.1,
            location: 0,
            distance: 100,
            maxPatternLength: 32,
            minMatchCharLength: 1,
            keys: ['first_name', 'last_name', 'nickname', 'maiden_name']
        };
        _this4.fuse = new Fuse(props.graph.nodes, options);
        return _this4;
    }

    _createClass(TrojstenGraph, [{
        key: 'componentDidMount',
        value: function componentDidMount() {
            var _this5 = this;

            window.addEventListener('resize', this.updateDimensions);
            this.canvas = this.refs.canvas;
            this.searchInput = this.refs.search_query;
            this.renderer = new GraphRenderer(this.canvas);
            this.simulation = new GraphSimulation(this.canvas);
            this.simulation.setData(this.props.graph);
            this.simulation.render = this.renderer.renderGraph;
            this.filter.onFilterUpdate(function (graph) {
                return _this5.setData(graph);
            });
            this.filter.filterGraph();
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
                React.createElement(GraphFilterPanel, { filter: this.filter }),
                this.getSidebar()
            );
        }
    }]);

    return TrojstenGraph;
}(React.Component);

function initializeGraph(graph) {
    ReactDOM.render(React.createElement(TrojstenGraph, { graph: graph }), document.getElementById('container'));
}