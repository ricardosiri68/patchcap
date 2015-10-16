import {Configuration} from './configuration'; 
import {inject} from 'aurelia-framework';
import {HttpClient} from 'aurelia-fetch-client';
import 'fetch';

@inject(Configuration, HttpClient)
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
    return this.http.fetch('devices', {credentials: 'include'})
      .then(response => response.json())
      .then(devices => this.devices = devices);
  }

  newDevice(){
    this.device = {};
    this.headingModal= "Agregar Dispositivo";
    this.showingNewDevice = true;
    this.showing = true;    
    this.submit = function () { this.http.fetch('devices', { method: "POST", 
                                                              body: JSON.stringify({ name: this.device.name,
                                                                                      ip: this.device.ip}),
                                                              credentials: 'include'
                                                            });                  
                                  window.location.reload();
                              }
  } 

  modify(index){
    this.headingModal= "Modificar Dispositivo";
    this.device = this.devices[index];
    this.showingNewDevice = false;
    this.showing = true;    
    this.submit = function () { this.http.fetch('devices/'+this.devices[index].id , 
                                                  { method: "PUT", body: JSON.stringify({ name: this.device.name,
                                                                                          ip: this.device.ip}),
                                                    credentials: 'include'
                                                  });      
                                  window.location.reload();
                              }
  }

  del(index){
    this.http.fetch('devices/'+this.devices[index].id , {method: "DELETE", credentials: 'include'} );
    window.location.reload()
  } 

  closeModal(){   
    this.showing = false;
  }

}
