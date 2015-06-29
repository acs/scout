'use strict';

// Declare app level module which depends on views, and components

var dashApp = angular.module('scoutApp', [
  'ngRoute',
  'datasourceControllers',
  'ui.bootstrap'
]);

dashApp.config(['$routeProvider', function($routeProvider) {
  $routeProvider.
      when('/scout', {
          templateUrl: 'scout/global.html',
          controller: 'ScoutGlobalCtrl'
      }).
      when('/scout_mustache', {
          templateUrl: 'scout/global_mustache.html',
          controller: 'ScoutGlobalCtrl'
      }).
      otherwise({redirectTo: '/scout'});
}]);