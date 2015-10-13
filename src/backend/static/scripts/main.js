(function() {
  'use strict';
  angular.module('app', ['ui.router', 'app.views']).config([
    '$stateProvider', '$urlRouterProvider', function($stateProvider, $urlRouterProvider) {
      var FORM_CONTENT_TYPE;
      FORM_CONTENT_TYPE = {
        'Content-Type': 'application/x-www-form-urlencoded'
      };
      $urlRouterProvider.otherwise('/');
      return $stateProvider.state('app', {
        url: '/',
        resolve: {
          user: [
            '$http', function($http) {
              return $http.post('/api/user/me').then(function(response) {
                return response.data;
              }, function(response) {
                return {};
              });
            }
          ]
        },
        templateUrl: 'app.html',
        controller: [
          '$scope', 'user', function($scope, user) {
            $scope.APP_NAME = 'backend';
            return $scope.user = user;
          }
        ]
      }).state('login', {
        url: '/login',
        templateUrl: 'user/login_form.html',
        controller: [
          '$scope', '$http', '$state', function($scope, $http, $state) {
            $scope.form = {};
            $scope.errors = {};
            return $scope.doLogin = function() {
              return $http.post('/api/login', $.param($scope.form), {
                headers: FORM_CONTENT_TYPE
              }).then(function(response) {
                return $state.go('app', {}, {
                  reload: true
                });
              }, function(response) {
                if (response.status === 400) {
                  return $scope.errors = response.data;
                } else {
                  return $scope.errors = {
                    login_id: "wrong id or password"
                  };
                }
              });
            };
          }
        ]
      }).state('logout', {
        url: '/logout',
        template: 'logging out...',
        controller: [
          '$http', '$state', function($http, $state) {
            return $http.post('/api/logout', {}, {
              headers: FORM_CONTENT_TYPE
            })["finally"](function(response) {
              return $state.go('app', {}, {
                reload: true
              });
            });
          }
        ]
      }).state('register', {
        url: '/register',
        templateUrl: 'user/register.html',
        controller: [
          '$scope', '$http', '$state', function($scope, $http, $state) {
            $scope.form = {};
            $scope.errors = {};
            return $scope.doRegister = function() {
              return $http.post('/api/user/register', $.param($scope.form), {
                headers: FORM_CONTENT_TYPE
              }).then(function(response) {
                return $state.go('app', {}, {
                  reload: true
                });
              }, function(response) {
                if (response.status === 400) {
                  return $scope.errors = response.data;
                } else {
                  return $scope.errors = {
                    email: "could not register with this email"
                  };
                }
              });
            };
          }
        ]
      }).state('activate', {
        url: '/activate/:cmdId',
        templateUrl: 'user/activate.html',
        controller: [
          '$scope', '$http', '$state', function($scope, $http, $state) {
            $scope.form = {};
            $scope.form.command_id = $state.params.cmdId;
            return $scope.doActivate = function() {
              return $http.post('/api/user/activate', $.param($scope.form), {
                headers: FORM_CONTENT_TYPE
              }).then(function(result) {
                return $state.go('app', {}, {
                  reload: true
                });
              }, function(response) {
                if (response.status === 400) {
                  return $scope.errors = response.data;
                } else {
                  return $scope.errors = {
                    email: "could not create your account"
                  };
                }
              });
            };
          }
        ]
      }).state('forgot', {
        url: '/forgot',
        templateUrl: 'user/forgot.html',
        controller: [
          '$scope', '$http', '$state', function($scope, $http, $state) {
            $scope.form = {};
            $scope.errors = {};
            return $scope.doForgot = function() {
              return $http.post('/api/user/forgot', $.param($scope.form), {
                headers: FORM_CONTENT_TYPE
              }).then(function(response) {
                return $state.go('app', {}, {
                  reload: true
                });
              }, function(response) {
                if (response.status === 400) {
                  return $scope.errors = response.data;
                } else {
                  return $scope.errors = {
                    email: "could not reset password with this email"
                  };
                }
              });
            };
          }
        ]
      }).state('reset', {
        url: '/reset/:cmdId',
        templateUrl: 'user/reset.html',
        controller: [
          '$scope', '$http', '$state', function($scope, $http, $state) {
            $scope.form = {};
            $scope.form.command_id = $state.params.cmdId;
            return $scope.doReset = function() {
              return $http.post('/api/user/reset', $.param($scope.form), {
                headers: FORM_CONTENT_TYPE
              }).then(function(result) {
                return $state.go('app', {}, {
                  reload: true
                });
              }, function(response) {
                if (response.status === 400) {
                  return $scope.errors = response.data;
                } else {
                  return $scope.errors = {
                    email: "could not reset your password"
                  };
                }
              });
            };
          }
        ]
      });
    }
  ]);

}).call(this);
