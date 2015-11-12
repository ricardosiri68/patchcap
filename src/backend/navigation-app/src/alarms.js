import {Config} from './config'; 
import {inject} from 'aurelia-framework';
import {HttpClient} from 'aurelia-fetch-client';
import 'fetch';

@inject(Config, HttpClient)
export class Alarms{
  heading = 'Alarmas';
  alarms = [];
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
    this.alarms= [];
    return this.http.fetch('alarms', {credentials: 'include'}) 
             .then(response => response.json())      
             .then(alarms => this.alarms = alarms)
             .catch(function(err) {
                    console.log('Fetch Error :-S', err);                
                    if(err.status == 403){
                        localStorage.removeItem("auth_token");  
                        window.location.reload();
                    }
              });
  }

  newAlarm(){    
    this.showing = false;
  	this.alarm = {};
    this.getTypeAlarms();
  	this.headingModal= "Agregar Alarmas";
  	this.showingNewAlarm = true;
    this.showing = true;    
    this.submit = function () { this.http.fetch('alarms' , { method: "POST", 
                                                            body: JSON.stringify({ profiles:[{id:this.alarm.profiler}]
                                                                                    , name: this.alarm.name}),
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
    this.getTypeAlarms();
    this.headingModal= "Modificar Alarma";
    this.alarm = this.alarms[index];
    this.showingNewAlarm = false;
    this.showing = true;    
    this.submit = function () { this.http.fetch('alarms/'+this.alarms[index].id, 
                                                  { method: "PUT",
												    	                      body: JSON.stringify({profiles:[{id:this.alarm.profiler}]
                                                                            , name: this.alarm.name}),
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
  	if(confirm('Desea eliminar esta alarma. Usted esta seguro? ')){
          this.http.fetch('alarms/'+this.alarms[index].id , {method: "DELETE", credentials: 'include'} );
    	    this.activate();
  	}    
  } 

  closeModal(){  	
    this.showing = false;
  }

  getTypeAlarms(){
    this.typeAlarms =[];
    this.http.fetch('profiles', {credentials: 'include'}) 
             .then(response => response.json())      
             .then(typeAlarms => this.typeAlarms = typeAlarms)
             .catch(function(err) {
                    console.log('Fetch Error :-S', err);                
                    if(err.status == 403){
                        localStorage.removeItem("auth_token");  
                        window.location.reload();
                    }
              });
  }
}
