'use strict';

var datasourceControllers = angular.module('datasourceControllers', []);

datasourceControllers.controller('ScoutGlobalCtrl', ['$scope', '$sce','$timeout',
  function ($scope, $sce, $timeout) {
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

    if (Events.scout === undefined) {
        // If the data is not yet available, subscribe not data ready event
        Events.data_ready(data_ready);
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