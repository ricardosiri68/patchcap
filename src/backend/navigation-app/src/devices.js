import {Config} from './config'; 
import {inject} from 'aurelia-framework';
import {HttpClient} from 'aurelia-fetch-client';
import 'fetch';

@inject(Config, HttpClient)
export class Devices{
  heading = 'Dispositivos';
  devices = [];
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
    this.devices = [];
    return this.http.fetch('devices', {credentials: 'include'})
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

  newDevice(){
    this.showing = false;
    this.device = {};
    this.headingModal= "Agregar Dispositivo";
    this.showingNewDevice = true;
    this.showing = true;        
    this.submit = function () { this.http.fetch('devices', { method: "POST", 
                                                              body: JSON.stringify({ name: this.device.name,
                                                                                      ip: this.device.ip,
                                                                                      instream: this.device.instream,
                                                                                      outstream: this.device.outstream,
                                                                                      username: this.device.username,
                                                                                      password: this.device.password,
                                                                                      roi: this.device.roi
                                                                                    }),
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
    this.headingModal= "Modificar Dispositivo";
    this.device = this.devices[index];
    this.showingNewDevice = false;
    this.showing = true;        
    this.submit = function () { this.http.fetch('devices/'+this.devices[index].id , 
                                                  { method: "PUT", body: JSON.stringify({ name: this.device.name,
                                                                                          ip: this.device.ip,
                                                                                          instream: this.device.instream,
                                                                                          outstream: this.device.outstream,
                                                                                          username: this.device.username,
                                                                                          password: this.device.password,
                                                                                          roi: this.device.roi
                                                                                        }),
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
    this.http.fetch('devices/'+this.devices[index].id , {method: "DELETE", credentials: 'include'} )
                    .catch(function(err) {
                              console.log('Fetch Error :-S', err);                
                              if(err.status == 403){
                                localStorage.removeItem("auth_token");  
                                window.location.reload();
                              }
                    });
    this.activate();
  } 

  closeModal(){   
    this.showing = false;
  }

}
