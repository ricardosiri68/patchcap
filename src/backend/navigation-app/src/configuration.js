import 'bootstrap';
import {inject} from 'aurelia-framework';
import {Redirect} from 'aurelia-router';
import 'fetch';

export class Configuration {
	heading = 'Configuracion';

  configureRouter(config, router){   
   

    config.map([
      { route: ['','users'],name: 'users',        moduleId: 'users',        nav: true,  title:'Usuarios'},
      { route: 'alarms',   name: 'alarms',      moduleId: 'alarms',      nav: true,  title:'Alarmas'},
      { route: 'devices',   name: 'devices',      moduleId: 'devices',      nav: true,  title:'Dispositivos'}
    ]);

    this.router = router;   
  }  
  
}
