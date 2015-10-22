import {Configuration} from './configuration'; 
import {inject} from 'aurelia-framework';
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

  activate(){
    this.users= [];
    return this.http.fetch('users', {credentials: 'include'}) 
             .then(response => response.json())      
             .then(users => this.users = users)
             .catch(function(err) {
                    console.log('Fetch Error :-S', err);                
                    if(err.status == 403){
                        localStorage.removeItem("auth_token");  
                        window.location.reload();
                    }
              });
  }

  newUser(){    
  	this.user = {};
    this.getProfiles();
  	this.headingModal= "Agregar Usuario";
  	this.showingNewUser = true;
    this.showing = true;    
    this.submit = function () { this.http.fetch('users' , { method: "POST", 
                                                            body: JSON.stringify({ profiles:[{id:this.user.profiler}]
                                                                                    ,username: this.user.username
                                                                                    , name: this.user.name
                                                                                    , email: this.user.email
                                                                                    , password: this.user.password}),
                                                            credentials: 'include'
                                                })
                                                .catch(function(err) {
                                                  console.log('Fetch Error :-S', err);                
                                                  if(err.status == 403){
                                                    localStorage.removeItem("auth_token");  
                                                    window.location.reload();
                                                  }
                                                });                                
                                this.activate();
                                this.showing = false;
							                 }
  } 

  modify(index){
    this.getProfiles();
    this.headingModal= "Modificar Usuario";
    this.user = this.users[index];
    this.showingNewUser = false;
    this.showing = true;    
    this.submit = function () { this.http.fetch('users/'+this.users[index].id, 
                                                  { method: "PUT",
												    	                      body: JSON.stringify({profiles:[{id:this.user.profiler}]
                                                                            , name: this.user.name
                                                                            , email: this.user.email}),
                                                    credentials: 'include'
												                        })
                                                .catch(function(err) {
                                                  console.log('Fetch Error :-S', err);                
                                                  if(err.status == 403){
                                                    localStorage.removeItem("auth_token");  
                                                    window.location.reload();
                                                  }
                                                });
                                 this.activate();
                                 this.showing = false;
							                 }
  }

  del(index){
  	if(confirm('Desea eliminar este usuario. Usted esta seguro? ')){
          this.http.fetch('users/'+this.users[index].id , {method: "DELETE", credentials: 'include'} );
    	    this.activate();
  	}    
  } 

  closeModal(){  	
    this.showing = false;
  }

  getProfiles(){
    this.profiles =[];
    this.http.fetch('profiles', {credentials: 'include'}) 
             .then(response => response.json())      
             .then(profiles => this.profiles = profiles)
             .catch(function(err) {
                    console.log('Fetch Error :-S', err);                
                    if(err.status == 403){
                        localStorage.removeItem("auth_token");  
                        window.location.reload();
                    }
              });
  }

}
