var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _toConsumableArray(arr) { if (Array.isArray(arr)) { for (var i = 0, arr2 = Array(arr.length); i < arr.length; i++) { arr2[i] = arr[i]; } return arr2; } else { return Array.from(arr); } }

function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var PersonDetail = function (_React$Component) {
    _inherits(PersonDetail, _React$Component);

    function PersonDetail() {
        var _ref;

        var _temp, _this, _ret;

        _classCallCheck(this, PersonDetail);

        for (var _len = arguments.length, args = Array(_len), _key = 0; _key < _len; _key++) {
            args[_key] = arguments[_key];
        }

        return _ret = (_temp = (_this = _possibleConstructorReturn(this, (_ref = PersonDetail.__proto__ || Object.getPrototypeOf(PersonDetail)).call.apply(_ref, [this].concat(args))), _this), _this.listMemberships = function (name, memberships) {
            return React.createElement(
                'div',
                null,
                React.createElement(
                    'h4',
                    null,
                    name
                ),
                React.createElement(
                    'ul',
                    null,
                    memberships.map(function (membership) {
                        return React.createElement(
                            'li',
                            { key: membership.group_name },
                            React.createElement(
                                'b',
                                null,
                                membership.group_name,
                                ' from ',
                                dateToString(membership.date_started),
                                ' to ',
                                dateToString(membership.date_ended)
                            )
                        );
                    })
                )
            );
        }, _temp), _possibleConstructorReturn(_this, _ret);
    }

    _createClass(PersonDetail, [{
        key: 'render',
        value: function render() {
            var person = this.props.person;

            var school_categories = [enums.Categories.elementarySchool, enums.Categories.highSchool, enums.Categories.university];
            var school_memberships = person.memberships.filter(function (membership) {
                return school_categories.includes(membership.group_category);
            });
            var seminar_memberships = person.memberships.filter(function (membership) {
                return membership.group_category === enums.Categories.seminar;
            });
            var other_memberships = person.memberships.filter(function (membership) {
                return membership.group_category === enums.Categories.other;
            });
            return React.createElement(
                'div',
                { className: 'info-sidebar' },
                React.createElement(
                    'div',
                    null,
                    React.createElement(
                        'h2',
                        null,
                        person.first_name,
                        ' ',
                        person.last_name
                    )
                ),
                React.createElement(
                    'div',
                    null,
                    React.createElement(
                        'ul',
                        null,
                        person.nickname && React.createElement(
                            'li',
                            null,
                            React.createElement(
                                'b',
                                null,
                                'Nickname: ',
                                person.nickname
                            )
                        ),
                        React.createElement(
                            'li',
                            null,
                            React.createElement(
                                'b',
                                null,
                                'Born on ',
                                dateToString(new Date(person.birth_date))
                            )
                        )
                    )
                ),
                seminar_memberships.length > 0 && this.listMemberships('Seminar memberships', seminar_memberships),
                school_memberships.length > 0 && this.listMemberships('School memberships', school_memberships),
                other_memberships.length > 0 && this.listMemberships('Other memberships', other_memberships)
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
                    'div',
                    null,
                    React.createElement(
                        'ul',
                        null,
                        this.props.relationship.statuses.map(function (status, i) {
                            return React.createElement(
                                'li',
                                { key: i },
                                React.createElement(
                                    'b',
                                    null,
                                    labels.StatusChoices[status.status],
                                    ' from ',
                                    dateToString(status.date_start),
                                    ' to ',
                                    dateToString(status.date_end)
                                )
                            );
                        })
                    )
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
                { key: label, className: 'filter-group' },
                React.createElement(
                    'h4',
                    null,
                    label
                ),
                React.createElement(
                    'table',
                    { className: 'table-borderless' },
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
                                        React.createElement('input', { key: option.name, type: 'checkbox',
                                            checked: _this3.state[option.name] === true ? 'checked' : '',
                                            name: option.name, onChange: _this3.handleInputChange, id: option.name
                                        }),
                                        React.createElement(
                                            'label',
                                            { htmlFor: option.name },
                                            React.createElement(
                                                'b',
                                                null,
                                                option.label
                                            )
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
                null,
                React.createElement(
                    'h3',
                    null,
                    'Filters'
                ),
                this.inputGroup('People', peopleFilters),
                this.inputGroup('Relationships', relationshipFilters)
            );
        }
    }]);

    return GraphFilterPanel;
}(React.Component);

var GraphSearch = function (_React$Component4) {
    _inherits(GraphSearch, _React$Component4);

    function GraphSearch(props) {
        _classCallCheck(this, GraphSearch);

        var _this4 = _possibleConstructorReturn(this, (GraphSearch.__proto__ || Object.getPrototypeOf(GraphSearch)).call(this, props));

        _this4.search = function (e) {
            var simulation = _this4.props.parent.simulation;
            var fuse = new Fuse(simulation.nodes, _this4.options);
            simulation.nodes.forEach(function (node) {
                node.isSearchResult = false;
            });
            fuse.search(normalizeString(_this4.refs.search_query.value)).forEach(function (node) {
                node.isSearchResult = true;
            });
            var start = Date.now();
            function pulseSearchResults() {
                simulation.update();
                if (Date.now() - start < 3000) {
                    requestAnimationFrame(pulseSearchResults);
                } else {
                    simulation.nodes.forEach(function (node) {
                        node.isSearchResult = false;
                    });
                    simulation.update();
                }
            }
            pulseSearchResults();
        };

        _this4.options = {
            shouldSort: true,
            threshold: 0.1,
            location: 0,
            distance: 100,
            maxPatternLength: 32,
            minMatchCharLength: 1,
            keys: ['searchAttributes.first_name', 'searchAttributes.last_name', 'searchAttributes.nickname', 'searchAttributes.maiden_name']
        };
        return _this4;
    }

    _createClass(GraphSearch, [{
        key: 'render',
        value: function render() {
            return React.createElement(
                'div',
                null,
                React.createElement(
                    'h3',
                    null,
                    'Search'
                ),
                React.createElement('input', { ref: 'search_query', type: 'text', className: 'input-lg' }),
                React.createElement(
                    'button',
                    { onClick: this.search, className: 'btn btn-default' },
                    'Find'
                )
            );
        }
    }]);

    return GraphSearch;
}(React.Component);

var GraphTimelinePanel = function (_React$Component5) {
    _inherits(GraphTimelinePanel, _React$Component5);

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

var TrojstenGraph = function (_React$Component6) {
    _inherits(TrojstenGraph, _React$Component6);

    function TrojstenGraph(props) {
        _classCallCheck(this, TrojstenGraph);

        var _this6 = _possibleConstructorReturn(this, (TrojstenGraph.__proto__ || Object.getPrototypeOf(TrojstenGraph)).call(this, props));

        _this6.getRelationship = function (firstPerson, secondPerson) {
            return _this6.props.graph.edges.find(function (edge) {
                return edge.source === firstPerson && edge.target === secondPerson || edge.source === secondPerson && edge.target === firstPerson;
            });
        };

        _this6.setData = function (graph) {
            _this6.simulation.setData(graph);
            _this6.renderer.setData(graph);
        };

        _this6.updateDimensions = function () {
            _this6.setState({ width: window.innerWidth, height: window.innerHeight });
            _this6.simulation.update();
        };

        _this6.canvasClick = function (e) {
            var clickedNode = _this6.simulation.nodeOnMousePosition(e.clientX, e.clientY);
            var selectedNodes = clickedNode ? prepend(_this6.state.selectedPeople, clickedNode).slice(0, 2) : [];
            _this6.setState({
                selectedPeople: selectedNodes
            });
            _this6.props.graph.nodes.forEach(function (node) {
                node.displayProps.selected = selectedNodes.includes(node);
            });
            _this6.simulation.update();
        };

        _this6.search = function (e) {
            _this6.props.graph.nodes.forEach(function (node) {
                node.isSearchResult = false;
            });
            _this6.fuse.search(_this6.searchInput.value.normalize('NFD')).forEach(function (node) {
                node.isSearchResult = true;
            });
            var start = Date.now();
            var self = _this6;
            function pulseSearchResults() {
                self.simulation.update();
                if (Date.now() - start < 3000) {
                    requestAnimationFrame(pulseSearchResults);
                } else {
                    self.props.graph.nodes.forEach(function (node) {
                        node.isSearchResult = false;
                    });
                    self.simulation.update();
                }
            }
            pulseSearchResults();
        };

        _this6.canvasMouseMove = function (e) {
            _this6.canvas.style.cursor = _this6.simulation.nodeOnMousePosition(e.clientX, e.clientY) ? 'pointer' : 'default';
        };

        _this6.getSidebar = function () {
            var firstPerson = _this6.state.selectedPeople[0],
                secondPerson = _this6.state.selectedPeople[1],
                relationship = void 0;
            if (firstPerson) {
                if (secondPerson && (relationship = _this6.getRelationship(firstPerson, secondPerson))) {
                    return React.createElement(RelationshipDetail, {
                        firstPerson: firstPerson,
                        secondPerson: secondPerson,
                        relationship: relationship
                    });
                }
                return React.createElement(PersonDetail, { person: firstPerson });
            }
        };

        _this6.state = {
            selectedPeople: [],
            width: window.innerWidth,
            height: window.innerHeight
        };

        _this6.filter = new GraphFilter(props.graph);
        return _this6;
    }

    _createClass(TrojstenGraph, [{
        key: 'componentDidMount',
        value: function componentDidMount() {
            var _this7 = this;

            window.addEventListener('resize', this.updateDimensions);
            this.canvas = this.refs.canvas;
            this.searchInput = this.refs.search_query;
            this.renderer = new GraphRenderer(this.canvas);
            this.simulation = new GraphSimulation(this.canvas);
            this.simulation.render = this.renderer.renderGraph;
            this.filter.onFilterUpdate(function (graph) {
                return _this7.setData(graph);
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
            var _this8 = this;

            return React.createElement(
                'div',
                null,
                React.createElement('canvas', { tabIndex: '1', ref: 'canvas', width: this.state.width, height: this.state.height,
                    onClick: this.canvasClick, onMouseMove: this.canvasMouseMove }),
                React.createElement(
                    'div',
                    { className: 'graph-toolbar' },
                    React.createElement(GraphFilterPanel, { filter: this.filter }),
                    React.createElement(GraphSearch, { parent: this }),
                    React.createElement(
                        'a',
                        { href: window.location.origin + '/logout/', className: 'btn btn-danger' },
                        'Log out'
                    )
                ),
                React.createElement(GraphTimelinePanel, { graph: this.props.graph, onChange: function onChange(e) {
                        _this8.filter.setCurrentTime(e);
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