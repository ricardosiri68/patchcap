import 'bootstrap';
import {inject} from 'aurelia-framework';
import {Redirect} from 'aurelia-router';
import 'fetch';

export class App {

  configureRouter(config, router){
    config.title = 'Mirich';    
    config.addPipelineStep('authorize', AuthorizeStep); 
    

    config.map([
      { route: 'login',         name: 'login',        moduleId: 'login',        nav: false, title:'Login'},
      { route: 'logout',        name: 'logout',       moduleId: 'logout',       nav: false, title:'Logout'},
      { route: ['','users'],    name: 'users',        moduleId: 'users',        nav: true,  title:'Usuarios', auth: true},
      { route: 'child-router',  name: 'child-router', moduleId: 'child-router', nav: true,  title:'Patentes', auth: true},
      { route: 'devices',       name: 'devices',      moduleId: 'devices',      nav: true,  title:'Dispositivos', auth: true}
    ]);

    this.router = router;   
  }  
  
}

//@inject(Configuration, HttpClient)
class AuthorizeStep {

  run(routingContext, next) {
        if (routingContext.nextInstructions.some(i => i.config.auth)) {
            var isLoggedIn = AuthorizeStep.isLoggedIn();
            if (!isLoggedIn) {
                return next.cancel(new Redirect('login'));
            }
        }
        return next();
  }

  static isLoggedIn(): boolean {
        var auth_token = localStorage.getItem("auth_token");
        return (typeof auth_token !== "undefined" && auth_token !== null);
  }

}