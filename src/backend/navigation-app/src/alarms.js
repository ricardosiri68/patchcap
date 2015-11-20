import {Config} from './config'; 
import {inject} from 'aurelia-framework';
import {HttpClient} from 'aurelia-fetch-client';
import 'fetch';

@inject(Config, HttpClient)
export class Alarms{
  heading = 'Alarmas';
  alarms = [];
  devices = [];
  typeAlarms =[];
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
    var there = this;
    return this.http.fetch('alarms', {credentials: 'include'}) 
             .then(response => response.json())      
             .then(alarms => this.alarms = alarms)
             .catch(function(err) {
                    console.log('Fetch Error :-S', err);                
                    if(err.status == 403){
                        localStorage.removeItem("auth_token");  
                        window.location.reload();
                    }else{
                      var result = [];       
                      result[0] = Object({id:1});
                      result[1] = Object({id:2});
                      var typeR = [];
                      typeR[0] = Object({id:1});
                      var alarm1 = Object({name:'Puesto 2', plate: 'EQF111,EQF112,EQF113', alarmType: typeR, devices: result});
                      var alarm2 = Object({name:'Puesto 1', plate: 'EQF222,EQF223,EQF224', alarmType: typeR, devices: result});
                      there.alarms.push(alarm1);
                      there.alarms.push(alarm2);
                    }
              });
  }

  newAlarm(){    
    this.showing = false;
  	this.alarm = {};
    this.getTypeAlarms();
    this.getDevices();
  	this.headingModal= "Agregar Alarmas";
  	//this.showingNewAlarm = true;
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
    this.getDevices();
    this.headingModal= "Modificar Alarma";
    this.alarm = this.alarms[index];
    //this.showingNewAlarm = false;
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
    if(this.typeAlarms.length == 0){
    var there = this;
    this.http.fetch('alarms/classes', {credentials: 'include'}) 
             .then(response => response.json())      
             .then(typeAlarms => this.typeAlarms = typeAlarms)
             .catch(function(err) {
                    console.log('Fetch Error :-S', err);                
                    if(err.status == 403){
                        localStorage.removeItem("auth_token");  
                        window.location.reload();
                    }else{
                        var alarmtype1 = Object({id: 1 , name: 'Lista Blanca'});
                        var alarmtype2 = Object({id: 2 , name: 'Lista Negra'});
                        there.typeAlarms.push(alarmtype1);
                        there.typeAlarms.push(alarmtype2);
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
}
