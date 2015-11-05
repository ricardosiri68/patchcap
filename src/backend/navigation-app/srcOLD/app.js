export class App {
  configureRouter(config, router){
    config.title = 'Mirich';
    //config.addPipelineStep('authorize', AuthorizeStep); auth: false, auth: true,
    config.map([
      { route: ['','welcome'],  name: 'welcome',      moduleId: 'welcome',      nav: false, title:'Login' }, 
      { route: 'users',         name: 'users',        moduleId: 'users',        nav: true,  title:'Usuarios' },
      { route: 'child-router',  name: 'child-router', moduleId: 'child-router', nav: true,  title:'Patentes' },
      { route: 'devices',       name: 'devices',      moduleId: 'devices',      nav: true,  title:'Dispositivos' }
    ]);

    this.router = router;
  }
}
