'use strict';

var datasourceControllers = angular.module('datasourceControllers', []);

datasourceControllers.controller('ScoutGlobalCtrl',
        ['$scope', '$sce', '$http', '$q','$timeout',
  function ($scope, $sce, $http, $q, $timeout) {

    var events_page = 30; // Number of events per virtual page

    function data_ready(events) {
        Events.set_events(events);
        $scope.scout_events = Events.get_timeline_events(undefined, events_page);
        $scope.keywords = Events.keywords;
        $scope.scout_events_raw = Events.scout;
        $scope.filter = {"dss":undefined, // data sources
                         "subject":undefined,
                         "body":undefined,
                         "author":undefined};
    }

    function load_data_limited(config) {
        // First try to load the events using limited events files

        var urlCalls = [];
        angular.forEach (config.backends, function (backend, i) {
            var filename = "/data/json/" + config.keywords.join() + "-" + backend;
            filename += "-"+config.limit+".json";
            // console.log("Loading file " + filename);
            urlCalls.push($http({method:'GET',url:filename}));
        });
        $q.all(urlCalls)
            .then(
              function(results) {
                  // The keywords are the same for all backends
                  Events.keywords = config.keywords;
                  var events_scout = {};
                  angular.forEach (results, function (result, i) {
                      angular.extend(events_scout, result.data.events);
                  });
                  data_ready(events_scout);
                  load_all_data(config);
              },
              function(errors) {
                  console.log("Error loading events files ...")
                  console.log(errors);
              }
            );
    }

    $scope.showFilterEvents = function() {
        // Show events using filters defined and with pagination
        // for infinite scroll

        if ($scope.scout_events === undefined) {
            return;
        }

        var date_to, date_from;

        var dss = {};
        if ($scope.filter) {
            dss = $scope.filter.dss;
        }
        var dss_to_include;

        if (! angular.equals({}, dss)) {
            dss_to_include = [];
            // Filter specific data sources
            angular.forEach(dss, function(include, ds) {
                if (include) {
                    dss_to_include.push(ds);
                }
            });
        }

        if (Date.parse($scope.dt_from) !== Date.parse($scope.date_min) ||
                Date.parse($scope.dt_to) !== Date.parse($scope.date_max)) {
            // Filter using dates
            var date_from = new Date(Date.parse($scope.dt_from));
            var date_to = new Date(Date.parse($scope.dt_to));
        }

        var limit = $scope.scout_events.length + events_page;

        $scope.scout_events =
            Events.get_timeline_events(dss_to_include, limit,
                                       $scope.filter_text, date_from, date_to);
    };

    function load_all_data(config) {
        // Load all events
        var filename = "/data/json/" + config.keywords.join() + ".json";
        // console.log("Loading file " + filename);
        $http({method:'GET', url:filename}).
        success(function(data,status, headers, config){
            Events.set_events(data.events);
            $scope.scout_events_raw = Events.scout;
        }).
        error(function(data,status,headers,config){
            $scope.error = "Can not load " + filename;
            console.log(data);
        });
    }

    $scope.parseBody = function(body, keyword) {
        var limit = 80;
        var res = "";
        if (body !== null) {
            res = $sce.trustAsHtml(Events.highlightLimit(body, keyword, limit));
        }
        return res;
    };

    $scope.$watch('filter.dss', function (newVal, oldVal) {
        if (newVal === undefined) {
            return;
        }
        $scope.scout_events = [];
        $scope.showFilterEvents();
    }, true); // <-- objectEquality

    $scope.doSearch = function() {
        $scope.showFilterEvents();
    }

    $scope.selectCategory = function() {
        var category_data;

        // console.log("Loading category " + $scope.category)
        angular.forEach ($scope.categories, function (category) {
            if (category.name === $scope.category) {
                category_data = category;
                return false;
            }
        });
        if (category_data) load_data_limited(category_data);
    }

    function load_categories(categories_url) {
        $http({method:'GET',url:categories_url})
        .success(function(categories, status, headers, config) {
            $scope.categories = categories;
            angular.forEach (categories, function (category) {
                // Show by default the first category
                $scope.category = category.name;
                load_data_limited(category);
                return false;
            });
        }).
        error(function(data,status,headers,config){
            $scope.error = data;
            console.log(data);
        });
    }

    $scope.getEventAuthor = function(author_html) {
        var url = $sce.trustAsHtml(author_html);
        return url;
    };

    function scout_start() {
        var categories = "/data/json/scout-categories.json";
        // The JSON file could be passed as param
        if (document.URL.split('?').length > 1) {
            var param = document.URL.split('?')[1].split("&")[0].split("=");
            if (param[0] === "categories_file") {
                categories = "/data/json/"+param[1];
            }
        }

        load_categories(categories);

        dt_init();
    }

    function dt_init() {
        $scope.date_min = Events.get_oldest_event_date();
        $scope.date_max = new Date();
        $scope.dt_from = $scope.date_min;
        $scope.dt_to = $scope.date_max;
    }

    $scope.$watch('scout_events_raw', function (newVal, oldVal) {
        if (newVal === undefined) {
            return;
        }
        $scope.date_min = Events.get_oldest_event_date();
        $scope.dt_from = $scope.date_min;
    }, true); // <-- objectEquality

    $scope.$watch('dt_from', function (newVal, oldVal) {
        if (newVal === undefined) {
            return;
        }
        $scope.showFilterEvents();
    }, true); // <-- objectEquality

    $scope.$watch('dt_to', function (newVal, oldVal) {
        if (newVal === undefined) {
            return;
        }
        $scope.showFilterEvents();
    }, true); // <-- objectEquality

    $scope.open_from = function($event) {
        $scope.status.opened_from = true;
    };

    $scope.open_to = function($event) {
        $scope.status.opened_to = true;
    };

    $scope.dateOptions = {
        formatYear: 'yy',
        startingDay: 1
    };

    $scope.status = {
        opened_from: false,
        opened_to: false
    };

    // Init the interface
    scout_start();

}]);