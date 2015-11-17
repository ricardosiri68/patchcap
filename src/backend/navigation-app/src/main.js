import 'bootstrap';

export function configure(aurelia) {
  aurelia.use
    .standardConfiguration()
    .developmentLogging();

  //Uncomment the line below to enable animation.
  //aurelia.use.plugin('aurelia-animator-css');

  //Anyone wanting to use HTMLImports to load views, will need to install the following plugin.
  //aurelia.use.plugin('aurelia-html-import-template-loader')

  // My filter
  //aurelia.globalizeResources('./my-filter');
  // Install the plugin
  aurelia.use.plugin('aurelia-bs-modal');
  //aurelia.use.plugin('socket.io-client');

  
  aurelia.start().then(a => a.setRoot());     
}
