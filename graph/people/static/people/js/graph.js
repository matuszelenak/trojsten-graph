var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _toConsumableArray(arr) { if (Array.isArray(arr)) { for (var i = 0, arr2 = Array(arr.length); i < arr.length; i++) { arr2[i] = arr[i]; } return arr2; } else { return Array.from(arr); } }

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

        _this3.inputGroup = function (label, optionGroup) {
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
                        optionGroup.map(function (options, i) {
                            return React.createElement(
                                'tr',
                                { key: i },
                                options.map(function (option) {
                                    return React.createElement(
                                        'td',
                                        { key: option.name },
                                        React.createElement('input', { key: option.name, type: 'checkbox', checked: _this3.state[option.name] === true ? 'checked' : '',
                                            name: option.name, onChange: _this3.handleInputChange, id: option.name
                                        }),
                                        React.createElement(
                                            'label',
                                            { htmlFor: option.name },
                                            option.label
                                        )
                                    );
                                })
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
            var peopleFilters = this.filter.getFilterOptions('isKSP', 'isKMS', 'isFKS', 'notTrojsten').map(function (arr) {
                return [arr];
            });
            var relationshipFilters = [this.filter.getFilterOptions('isCurrentSerious', 'isOldSerious'), this.filter.getFilterOptions('isCurrentRumour', 'isOldRumour'), this.filter.getFilterOptions('isBloodBound')];
            return React.createElement(
                'div',
                { className: 'graph-filter' },
                this.inputGroup('People', peopleFilters),
                this.inputGroup('Relationships', relationshipFilters)
            );
        }
    }]);

    return GraphFilterPanel;
}(React.Component);

var GraphTimelinePanel = function (_React$Component4) {
    _inherits(GraphTimelinePanel, _React$Component4);

    function GraphTimelinePanel(props) {
        _classCallCheck(this, GraphTimelinePanel);

        return _possibleConstructorReturn(this, (GraphTimelinePanel.__proto__ || Object.getPrototypeOf(GraphTimelinePanel)).call(this, props));
    }

    _createClass(GraphTimelinePanel, [{
        key: 'componentDidMount',
        value: function componentDidMount() {
            var slider = document.getElementById('time-setter');
            var event_dates = this.props.graph.edges.map(function (edge) {
                return edge.statuses.map(function (status) {
                    return [status.date_start, status.date_end];
                });
            }).flat(2);
            event_dates = [].concat(_toConsumableArray(new Set(event_dates))).filter(function (x) {
                return x !== null;
            }).sort(function (a, b) {
                return a - b;
            });

            var ranges = {};
            var min_date = event_dates[0].getTime(),
                max_date = event_dates[event_dates.length - 1].getTime();
            if (event_dates.length > 2) {
                event_dates.slice(1, -1).reduce(function (ranges, date) {
                    var percentage = (date - min_date) / (max_date - min_date) * 100;
                    ranges[percentage + '%'] = date.getTime();
                    return ranges;
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
                    to: function to(ts) {
                        return dateToString(new Date(+ts));
                    }
                },
                range: ranges
            });
            var self = this;
            slider.noUiSlider.on('update', function (values, handle) {
                self.props.onChange(new Date(+values[handle]));
            });
        }
    }, {
        key: 'render',
        value: function render() {
            return React.createElement(
                'div',
                { className: 'timeline-panel' },
                React.createElement('div', { id: 'time-setter' })
            );
        }
    }]);

    return GraphTimelinePanel;
}(React.Component);

var TrojstenGraph = function (_React$Component5) {
    _inherits(TrojstenGraph, _React$Component5);

    function TrojstenGraph(props) {
        _classCallCheck(this, TrojstenGraph);

        var _this5 = _possibleConstructorReturn(this, (TrojstenGraph.__proto__ || Object.getPrototypeOf(TrojstenGraph)).call(this, props));

        _this5.getRelationship = function (firstPerson, secondPerson) {
            return _this5.props.graph.edges.find(function (edge) {
                return edge.source === firstPerson && edge.target === secondPerson || edge.source === secondPerson && edge.target === firstPerson;
            });
        };

        _this5.setData = function (graph) {
            _this5.simulation.setData(graph);
            _this5.renderer.setData(graph);
        };

        _this5.updateDimensions = function () {
            _this5.setState({ width: window.innerWidth, height: window.innerHeight });
            _this5.simulation.update();
        };

        _this5.canvasClick = function (e) {
            var clickedNode = _this5.simulation.nodeOnMousePosition(e.clientX, e.clientY);
            var selectedNodes = clickedNode ? prepend(_this5.state.selectedPeople, clickedNode).slice(0, 2) : [];
            _this5.setState({
                selectedPeople: selectedNodes
            });
            _this5.props.graph.nodes.forEach(function (node) {
                node.displayProps.selected = selectedNodes.includes(node);
            });
            _this5.simulation.update();
        };

        _this5.search = function (e) {
            _this5.props.graph.nodes.forEach(function (node) {});
        };

        _this5.canvasMouseMove = function (e) {
            _this5.canvas.style.cursor = _this5.simulation.nodeOnMousePosition(e.clientX, e.clientY) ? 'pointer' : 'default';
        };

        _this5.getSidebar = function () {
            var firstPerson = _this5.state.selectedPeople[0],
                secondPerson = _this5.state.selectedPeople[1],
                relationship = void 0;
            if (firstPerson) {
                if (secondPerson && (relationship = _this5.getRelationship(firstPerson, secondPerson))) {
                    return React.createElement(RelationshipDetail, {
                        firstPerson: firstPerson,
                        secondPerson: secondPerson,
                        relationship: relationship
                    });
                }
                return React.createElement(PersonDetail, { person: firstPerson });
            }
        };

        _this5.state = {
            selectedPeople: [],
            width: window.innerWidth,
            height: window.innerHeight
        };

        _this5.filter = new GraphFilter(props.graph);

        var options = {
            shouldSort: true,
            threshold: 0.1,
            location: 0,
            distance: 100,
            maxPatternLength: 32,
            minMatchCharLength: 1,
            keys: ['first_name', 'last_name', 'nickname', 'maiden_name']
        };
        _this5.fuse = new Fuse(props.graph.nodes, options);
        return _this5;
    }

    _createClass(TrojstenGraph, [{
        key: 'componentDidMount',
        value: function componentDidMount() {
            var _this6 = this;

            window.addEventListener('resize', this.updateDimensions);
            this.canvas = this.refs.canvas;
            this.searchInput = this.refs.search_query;
            this.renderer = new GraphRenderer(this.canvas);
            this.simulation = new GraphSimulation(this.canvas);
            this.simulation.render = this.renderer.renderGraph;
            this.filter.onFilterUpdate(function (graph) {
                return _this6.setData(graph);
            });
            this.filter.setCurrentTime(new Date());
        }
    }, {
        key: 'componentWillUnmount',
        value: function componentWillUnmount() {
            window.removeEventListener('resize', this.updateDimensions);
        }
    }, {
        key: 'render',
        value: function render() {
            var _this7 = this;

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
                React.createElement(GraphTimelinePanel, { graph: this.props.graph, onChange: function onChange(e) {
                        _this7.filter.setCurrentTime(e);
                    } }),
                this.getSidebar()
            );
        }
    }]);

    return TrojstenGraph;
}(React.Component);

function initializeGraph(graph) {
    preprocessGraph(graph);
    ReactDOM.render(React.createElement(TrojstenGraph, { graph: graph }), document.getElementById('container'));
}