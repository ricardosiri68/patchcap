'use strict'

angular.module('app', ['ui.router', 'app.views'])
.config(['$stateProvider', '$urlRouterProvider',
  ($stateProvider, $urlRouterProvider) ->

    FORM_CONTENT_TYPE = {'Content-Type': 'application/x-www-form-urlencoded'}
    $urlRouterProvider.otherwise('/')
    
    $stateProvider
    .state('app',
      url: '/'
      resolve:
        user: ['$http', ($http) ->
          $http.post('/api/user/me').then (response) ->
            response.data
          , (response) ->
            {}
          ]
      templateUrl: 'app.html'
      controller: ['$scope', 'user', ($scope, user) ->
        $scope.APP_NAME = 'backend'
        $scope.user = user
        ]
    )
    .state('login',
      url: '/login'
      templateUrl: 'user/login_form.html'
      controller: ['$scope', '$http', '$state', ($scope, $http, $state) ->
        $scope.form = {}
        $scope.errors = {}
        
        $scope.doLogin = () ->
          $http.post('/api/login', $.param($scope.form), {headers: FORM_CONTENT_TYPE}).then (response) ->
            $state.go('app', {}, {reload: true})
          , (response) ->
            if response.status == 400
              $scope.errors = response.data
            else
              $scope.errors =
                login_id: "wrong id or password"
      ]
      
    )
    .state('logout'
    url: '/logout'
    template:'logging out...'
    controller: ['$http', '$state', ($http, $state) ->
      $http.post('/api/logout', {}, {headers: FORM_CONTENT_TYPE}).finally (response) ->
        $state.go('app', {}, {reload: true})
      ]
    )
    .state('register',
      url: '/register'
      templateUrl:'user/register.html'
      controller: ['$scope', '$http', '$state', ($scope, $http, $state)->
        $scope.form = {}
        $scope.errors = {}

        $scope.doRegister = () ->
          $http.post('/api/user/register', $.param($scope.form), {headers: FORM_CONTENT_TYPE}).then (response) ->
            $state.go('app', {}, {reload: true})
          , (response) ->
            if response.status == 400
              $scope.errors = response.data
            else
              $scope.errors =
                email: "could not register with this email"
            
        ]
    )
    .state('activate',
      url: '/activate/:cmdId'
      templateUrl: 'user/activate.html'
      controller: ['$scope', '$http', '$state', ($scope, $http, $state) ->
        $scope.form = {}
        $scope.form.command_id = $state.params.cmdId

        $scope.doActivate = () ->
          $http.post('/api/user/activate', $.param($scope.form), {headers: FORM_CONTENT_TYPE}).then (result) ->
            $state.go('app', {}, {reload: true})
          , (response) ->
            if response.status == 400
              $scope.errors = response.data
            else
              $scope.errors =
                email: "could not create your account"
        
        ]
    )
    .state('forgot',
      url: '/forgot'
      templateUrl: 'user/forgot.html'
      controller: ['$scope', '$http', '$state', ($scope, $http, $state) ->
        $scope.form = {}
        $scope.errors = {}

        $scope.doForgot = () ->
          $http.post('/api/user/forgot', $.param($scope.form), {headers: FORM_CONTENT_TYPE}).then (response) ->
            $state.go('app', {}, {reload: true})
          , (response) ->
            if response.status == 400
              $scope.errors = response.data
            else
              $scope.errors =
                email: "could not reset password with this email"
            
        
        ]
    )
    .state('reset',
      url: '/reset/:cmdId'
      templateUrl: 'user/reset.html'
      controller: ['$scope', '$http', '$state', ($scope, $http, $state) ->
        $scope.form = {}
        $scope.form.command_id = $state.params.cmdId

        $scope.doReset = () ->
          $http.post('/api/user/reset', $.param($scope.form), {headers: FORM_CONTENT_TYPE}).then (result) ->
            $state.go('app', {}, {reload: true})
          , (response) ->
            if response.status == 400
              $scope.errors = response.data
            else
              $scope.errors =
                email: "could not reset your password"
        
     ]
    )
  ])
