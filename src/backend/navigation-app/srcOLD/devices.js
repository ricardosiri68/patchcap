import {Configuration} from './configuration'; 
import {inject} from 'aurelia-framework';
import {HttpClient} from 'aurelia-fetch-client';
import 'fetch';


@inject(Configuration, HttpClient)
export class Devices{
  heading = 'Dispositivos';
  devices = [];
  http;

  constructor(conf,http){
    http.configure(config => {
      config
        .useStandardConfiguration()
        .withBaseUrl(conf.baseUri);
    });

    this.http = http;
  }

  
  activate(){  
    return this.http.fetch('devices')
      .then(response => response.json())
      .then(devices => this.devices = devices);
  }  
}
