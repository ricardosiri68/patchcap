import {Config} from './config'; 
import {inject} from 'aurelia-framework';
import {HttpClient} from 'aurelia-fetch-client';
import 'fetch';

@inject(Config, HttpClient)
export class Users{
  heading = 'Usuarios';
  users = [];
  showing = false;
  profiles =[];
  devices =[];

  constructor(conf, http){
    http.configure(config => {
      config
        .useStandardConfiguration()
        .withBaseUrl(conf.baseUri);        

    });

    this.http = http;
    this.imgUsers = conf.imgUsers;
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
    this.showing = false;  
  	this.user = {};
    this.getProfiles();
    this.getDevices();
  	this.headingModal= "Agregar Usuario";
  	this.showingNewUser = true;
    this.showing = true;    
    this.submit = function () { 
                                var arrProfiles = this.optionsSelected('selectProfiles');
                                var arrDevices = this.optionsSelected('selectDevices');
                                this.http.fetch('users' , { method: "POST", 
                                                            body: JSON.stringify({ profiles: arrProfiles
                                                                                    , devices: arrDevices
                                                                                    , username: this.user.username
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
    this.showing = false;
    this.getProfiles();
    this.getDevices();
    this.headingModal= "Modificar Usuario";
    this.user = this.users[index];        
    this.showingNewUser = false;
    this.showing = true;    
    this.submit = function () { var arrProfiles = this.optionsSelected('selectProfiles');
                                var arrDevices = this.optionsSelected('selectDevices');
                                this.http.fetch('users/'+this.users[index].id, 
                                                  { method: "PUT",
												    	                      body: JSON.stringify({profiles: arrProfiles
                                                                            , devices: arrDevices
                                                                            , name: this.user.name
                                                                            , username: this.user.username
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
    if(this.profiles.length == 0){
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

  getDevices(){
    if(this.devices.length == 0){
        this.http.fetch('devices', {credentials: 'include'}) 
             .then(response => response.json())      
             .then(devices => this.devices = devices)
             .catch(function(err) {
                    console.log('Fetch Error :-S', err);                
                    if(err.status == 403){
                        localStorage.removeItem("auth_token");  
                        window.location.reload();
                    }
              });
    }
  }

  optionsSelected( divSelect){
    var result = []; 
    var object = Object();
    $('#'+divSelect+' :selected').each(function(i, selected){ 
      object.id = $(selected).val(); 
      result[i] = object;
    });
    return result;
  }
}
