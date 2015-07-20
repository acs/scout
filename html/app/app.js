'use strict';

// Declare app level module which depends on views, and components

var dashApp = angular.module('scoutApp', [
  'ngRoute',
  'datasourceControllers',
  'ui.bootstrap',
  'infinite-scroll'
]);

dashApp.config(['$routeProvider', function($routeProvider) {
  $routeProvider.
      when('/scout', {
          templateUrl: 'scout/global.html',
          controller: 'ScoutGlobalCtrl'
      }).
      otherwise({redirectTo: '/scout'});
}]);