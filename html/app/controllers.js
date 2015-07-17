'use strict';

var datasourceControllers = angular.module('datasourceControllers', []);

datasourceControllers.controller('ScoutGlobalCtrl',
        ['$scope', '$sce','$timeout', '$http', '$q',
  function ($scope, $sce, $timeout, $http, $q) {
    function data_ready() {
        $scope.scout_events = Events.get_timeline_events();
        $scope.keyword = Events.keyword;
        $scope.scout_events_raw = Events.scout;
        $scope.filter = {"dss":undefined, // data sources
                         "subject":undefined,
                         "body":undefined,
                         "author":undefined};
        $timeout(function() {
            $scope.$apply(); // To be removed when data is loaded from angular
        });
    }

    function load_data_limited(config) {
        // First try to load the events using limited events files
        var backends = config.backends;
        var limit = config.limit;
        var urlCalls = [];
        angular.forEach (config.backends, function (backend, i) {
            var filename = "/data/json/" + config.keyword + "-" + backend;
            filename += "-"+config.limit+".json";
            console.log("Loading file " + filename);
            urlCalls.push($http({method:'GET',url:filename}));
        });
        $q.all(urlCalls)
        .then(
          function(results) {
              Events.scout = {};
              // The keyword is the same for all backends
              Events.keyword = results[0].data.keyword;
              Events.scout = {};
              angular.forEach (results, function (result, i) {
                  angular.extend(Events.scout, result.data.events);
              });
              data_ready();
          },
          function(errors) {
              console.log("Error loading events files ...")
              console.log(errors);
          }
        );
    }

    if (Events.scout === undefined) {
        // If the data is not yet available, subscribe not data ready event
        // Events.data_ready(data_ready);

        var scout_config = "/data/json/scout.json";
        // The JSON file could be passed as param
        if (document.URL.split('?').length > 1) {
            param = document.URL.split('?')[1].split("&")[0].split("=");
            if (param[0] === "events_file") {
                scout_config = "/data/json/"+param[1];
            }
        }

        $http({method:'GET',url:scout_config})
        .success(function(data,status,headers,config){
            load_data_limited(data);
        }).
        error(function(data,status,headers,config){
            $scope.error = data;
            console.log(data);
        });

    } else {
        data_ready();
    }

    $scope.$watch('filter.dss', function (newVal, oldVal) {
        if (newVal === undefined) {
            return;
        }
        $scope.filter_dss($scope.filter.dss);
    }, true); // <-- objectEquality

    $scope.getEventAuthor = function(author_html) {
        var url = $sce.trustAsHtml(author_html);
        return url;
    }

    $scope.parseBody = function(body, keyword) {
        var limit = 80;
        var res = "";
        if (body !== null) {
            res = $sce.trustAsHtml(Events.highlightLimit(body, keyword, limit));
        }
        return res;
    }

    $scope.filter_dss = function(dss) {
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

        $scope.scout_events = Events.get_timeline_events(dss_to_include);
    };

    $scope.filterBySubject = function(event) {
        if ($scope.filter_text === undefined) {
            return true;
        }
        var summary = event.summary.toLowerCase();
        if (event.body === null) {
            event.body = '';
        }
        var body = event.body.toLowerCase();
        var author = event.author.toLowerCase();
        var search = $scope.filter_text.toLowerCase();
        var found = (summary.indexOf(search) !== -1) ||
                    (author.indexOf(search) !== -1) ||
                    (body.indexOf(search) !== -1);
        return found;
    };
 }]);