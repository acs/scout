'use strict';

var datasourceControllers = angular.module('datasourceControllers', []);

datasourceControllers.controller('ScoutGlobalCtrl', ['$scope', '$sce',
  function ($scope, $sce) {
    Events.data_ready(function() {
        $scope.scout_events = Events.get_timeline_events();
        $scope.$apply(); // To be removed when data is loaded from angular
    });

    $scope.getEventAuthor = function(author_html) {
        var url = $sce.trustAsHtml(author_html);
        return url;
    }

    $scope.parseBody = function(body) {
        var limit = 80;
        var keyword = "centos";
        var res = "";
        if (body !== null) {
            res = $sce.trustAsHtml(Events.highlightLimit(body, keyword, limit));
        }
        return res;
    }
 }]);