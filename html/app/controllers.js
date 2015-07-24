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
            console.log("Loading file " + filename);
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

    $scope.paginateEvents = function() {
        // Add more events to implement infinite scroll
        // Add more events from Events.scout_all to Events.scout
        if ($scope.scout_events === undefined) {
            return;
        }
        var limit = $scope.scout_events.length + events_page;
        if ($scope.filter.dss !== undefined) {
            $scope.filter_dss($scope.filter.dss, limit);
        }
        else {
            $scope.scout_events =
                Events.get_timeline_events(undefined, limit, $scope.filter_text);
        }
    };

    function load_all_data(config) {
        // Load all events
        var filename = "/data/json/" + config.keywords.join() + ".json";
        console.log("Loading file " + filename);
        $http({method:'GET', url:filename}).
        success(function(data,status,headers,config){
            Events.set_events(data.events);
            $scope.scout_events_raw = Events.scout;
        }).
        error(function(data,status,headers,config){
            $scope.error = "Can not load " + filename;
            console.log(data);
        });
    }

    $scope.$watch('filter.dss', function (newVal, oldVal) {
        if (newVal === undefined) {
            return;
        }
        $scope.filter_dss($scope.filter.dss, events_page);
    }, true); // <-- objectEquality

    $scope.getEventAuthor = function(author_html) {
        var url = $sce.trustAsHtml(author_html);
        return url;
    };

    $scope.parseBody = function(body, keyword) {
        var limit = 80;
        var res = "";
        if (body !== null) {
            res = $sce.trustAsHtml(Events.highlightLimit(body, keyword, limit));
        }
        return res;
    };

    $scope.filter_dss = function(dss, limit) {
        // Filter data sources not included in dss array
        var dss_to_include = [];
        if (angular.equals({}, dss)) {
            // No filters defined
            return;
        }
        angular.forEach(dss, function(include, ds) {
            if (include) {
                dss_to_include.push(ds);
            }
        });

        $scope.scout_events =
            Events.get_timeline_events(dss_to_include, limit, $scope.filter_text);
    };

    $scope.doSearch = function() {
        $scope.paginateEvents();
    }

    $scope.selectCategory = function() {
        console.log("Loading category " + $scope.category)
        load_data_limited($scope.categories[$scope.category]);
    }

    function load_categories(categories_url) {
        $http({method:'GET',url:categories_url})
        .success(function(categories, status, headers, config) {
            $scope.categories = categories;
            angular.forEach (categories, function (category, name) {
                // Show by default the first category
                $scope.category = name;
                load_data_limited(category);
                return false;
            });
        }).
        error(function(data,status,headers,config){
            $scope.error = data;
            console.log(data);
        });
    }

    $scope.scout_start = function() {
        var categories = "/data/json/scout-categories.json";
        // The JSON file could be passed as param
        if (document.URL.split('?').length > 1) {
            var param = document.URL.split('?')[1].split("&")[0].split("=");
            if (param[0] === "categories_file") {
                categories = "/data/json/"+param[1];
            }
        }
        load_categories(categories);
    };

    $scope.scout_start();
}]);