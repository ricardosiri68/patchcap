var gulp = require('gulp');
var sass = require('gulp-sass');
var concat = require('gulp-concat');
var coffee = require('gulp-coffee');

var angularTemplates = require('gulp-angular-templatecache');

var STYLES = ['./styles/**/*.scss']; //main.css
var SCRIPTS = ['./scripts/**/*.coffee']; //main.js
var VIEWS = ['./views/**/*.html'];

var FOUNDATION_STYLE = [
    'bower_components/foundation/css/normalize.css',
    'bower_components/foundation/css/foundation.css'
];

var FOUNDATION_JS = [
    'bower_components/foundation/js/foundation.min.js',
    'bower_components/jquery/dist/jquery.min.js'
];


var VENDOR_JS = [
    'bower_components/angular/angular.min.js',
    'bower_components/angular-ui-router/release/angular-ui-router.min.js'
];


gulp.task('vendor', function(){
    return gulp.src(VENDOR_JS)
    .pipe(concat('vendor.js'))
    .pipe(gulp.dest('../static/scripts/'));
});


gulp.task('foundation-js', function(){
    return gulp.src(FOUNDATION_JS)
    .pipe(gulp.dest('../static/scripts/'));
});


gulp.task('foundation', function(){
    return gulp.src(FOUNDATION_STYLE)
    .pipe(concat('foundation.css'))
    .pipe(gulp.dest('../static/styles/'));
});


// sass
gulp.task('styles', ['foundation', 'foundation-js', 'modernizr'], function(){
    return gulp.src(STYLES)
    .pipe(sass())
    .pipe(concat('main.css'))
    .pipe(gulp.dest('../static/styles/'));
});

// modernizr
gulp.task('modernizr', function(){
    return gulp.src('bower_components/modernizr/modernizr.js')
    .pipe(gulp.dest('../static/scripts/'));
});


// coffee-script
gulp.task('scripts', ['vendor'], function(){
    return gulp.src(SCRIPTS)
    .pipe(coffee())
    .pipe(concat('main.js'))
    .pipe(gulp.dest('../static/scripts/'));
});

// views
gulp.task('views', function(){
    return gulp.src(VIEWS)
    .pipe(angularTemplates({module:'app.views', standalone:true}))
    .pipe(concat('views.js'))
    .pipe(gulp.dest('../static/scripts'));
});

gulp.task('watch', ['styles', 'scripts', 'views'], function(){
    gulp.watch(STYLES, ['styles']);
    gulp.watch(SCRIPTS, ['scripts']);
    gulp.watch(VIEWS, ['views']);

});

gulp.task('default', ['styles', 'scripts', 'views']);
