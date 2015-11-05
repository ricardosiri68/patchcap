import {Configuration} from './configuration'; 
import {inject} from 'aurelia-framework';
import {HttpClient} from 'aurelia-fetch-client';
import 'fetch';

@inject(Configuration, HttpClient)
export class Users{
  heading = 'Github Users';
  users = [];

  /*configureRouter(config, router){
    config.map([
      { route: 'addUser', name: 'addUser', moduleId: 'addUser', nav: false, title:'Agregar Usuario' },
      { route: 'modUser', name: 'modUser', moduleId: 'modUser', nav: false, title:'Modificar Usuario' }
    ]);

    this.router = router;
  }*/

  constructor(conf, http){
    http.configure(config => {
      config
        .useStandardConfiguration()
        .withBaseUrl(conf.baseUri);        

    });

    this.http = http;
  }

  activate(){
    return this.http.fetch('users')
      .then(response => response.json())
      .then(users => this.users = users);
  }

  del(index){
    this.http.fetch('users/'+this.users[index].id, {RequestMethod: "DELETE", headers: {  
      "Content-type": "Access-Control-Allow; charset=UTF-8"  
    },});
  }

  /*add(id){
    this.http.fetch('users/'+id, 
      {
      method: "POST", 
      body: JSON.stringify({
        email: this.email,
        password: this.password
      })
    })
  }*/
}
