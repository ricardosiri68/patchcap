import 'bootstrap';
import {inject} from 'aurelia-framework';
import {Redirect} from 'aurelia-router';
import {Config} from './config'; 
//import {HttpClient} from 'aurelia-fetch-client';
//import 'fetch';

export class App {

  configureRouter(config, router){
    config.title = 'Mirich';    
    config.addPipelineStep('authorize', AuthorizeStep); 
    

    config.map([
      { route: 'login',         name: 'login',        moduleId: 'login',        nav: false, title:'Login'},
      { route: 'logout',        name: 'logout',       moduleId: 'logout',       nav: false, title:'Logout'},
      { route: ['','desktop'],  name: 'desktop',      moduleId: 'desktop',      nav: false,  title:'Escritorio'   , auth: true},
      { route: 'configuration', name: 'configuration',moduleId: 'configuration',nav: true,  title:'Configuracion', auth: true},
      { route: 'users',     name: 'users',        moduleId: 'users',        nav: false,  title:'Usuarios',     auth: true},      
      { route: 'devices',   name: 'devices',      moduleId: 'devices',      nav: false,  title:'Dispositivos', auth: true} 
    ]);

    this.router = router;   
  }  
  
}

//@inject(Config, HttpClient )
class AuthorizeStep {

/*  constructor(conf, http){
      http.configure(config => {
          config.useStandardConfiguration().withBaseUrl(conf.baseUri);        
      });

      this.http = http;    
  } */

  run(routingContext, next) {
        if (routingContext.nextInstructions.some(i => i.config.auth)) {
            var isLoggedIn = AuthorizeStep.isLoggedIn();
            if (!isLoggedIn) {                                              
                return next.cancel(new Redirect('login'));
            }
            else{
              $('#userName').text(localStorage.getItem("user_name")).attr("href", "#/logout");
            }
        }
        return next();
  }

  static isLoggedIn(): boolean {
            /*return this.http.fetch('users/me' , { method: "POST" , credentials: 'include'}) 
                .then( function(response) {  
                          if (response.status !== 200) {  
                              console.log('Looks like there was a problem. Status Code: ' +  response.status);  
                                return false;  
                            }

                          response.json().then(function(data) {  
                            console.log(data);  
                            $('#userName').text(data.name).attr("href", "#/logout");
                            localStorage.setItem("user_name", data.name);               
                          });
                })
                .catch(function(err) {  
                    console.log('Fetch Error :-S', err);                
                    return false;
                });*/
      var auth_token = localStorage.getItem("auth_token");
      return (typeof auth_token !== "undefined" && auth_token !== null);
  }

}