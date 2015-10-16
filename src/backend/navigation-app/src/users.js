import {Configuration} from './configuration'; 
import {inject} from 'aurelia-framework';
import {Redirect} from 'aurelia-router';
import {HttpClient} from 'aurelia-fetch-client';
import 'fetch';

@inject(Configuration, HttpClient)
export class Users{
  heading = 'Usuarios';
  users = [];
  showing = false;

  constructor(conf, http){
    http.configure(config => {
      config
        .useStandardConfiguration()
        .withBaseUrl(conf.baseUri);        

    });

    this.http = http;    
    this.showing = false;
  }

  /*canActivate(){
    return this.http.fetch('users/me', {credentials: 'include'})
            .then(response => {this.data = response.content;})
            .catch(error => { console.log("pasa por aqui sin error");});

//return Promise.reject(new Redirect('/error')
            //.then(console.log(this.data));    
            //.then(response.status = 403 ? true: true);    
  }*/

  activate(){
    return this.http.fetch('users', {credentials: 'include'}) 
             .then(response => response.json())      
             .then(users => this.users = users);
  }

  newUser(){
  	this.user = {};
  	this.headingModal= "Agregar Usuario";
  	this.showingNewUser = true;
    this.showing = true;    
    this.submit = function () { this.http.fetch('users' , { method: "POST", 
                                                            body: JSON.stringify({username: this.user.username
                                                                                    , name: this.user.name
                                                                                    , email: this.user.email
                                                                                    , password: this.user.password}),
                                                            credentials: 'include'
                                                          });          							
                                window.location.reload();
							                 }
  } 

  modify(index){
    this.headingModal= "Modificar Usuario";
    this.user = this.users[index];
    this.showingNewUser = false;
    this.showing = true;    
    this.submit = function () { this.http.fetch('users/'+this.users[index].id, 
                                                  { method: "PUT",
												    	                      body: JSON.stringify({name: this.user.name, email: this.user.email}),
                                                    credentials: 'include'
												                          });      
  							                 window.location.reload();
							                 }
  }

  del(index){
  	if(confirm('Desea eliminar este usuario. Usted esta seguro? ')){
          this.http.fetch('users/'+this.users[index].id , {method: "DELETE", credentials: 'include'} );
    	    window.location.reload();
  	}    
  } 

  closeModal(){  	
    this.showing = false;
  }

}
