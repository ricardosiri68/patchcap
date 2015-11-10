import {Config} from './config'; 
import {I18N} from 'aurelia-i18n';
import io from 'socket.io-client';
import {inject} from 'aurelia-framework';


@inject(Config, I18N)
export class Desktop {
  patents;
  alarms;
  filterPatent = '';
  filterCamera = '';
  filterAlarm = '';
  config;
  showing = false;

  constructor(conf, i18n) {

    //localStorage.removeItem('patents');
    // Put the object into storage        
    //localStorage.setItem('patents', JSON.stringify(this.patents));
    this.config = conf;
    this.i18n = i18n;
    console.log(this.i18n.getLocale());
    

    //this.patents = JSON.parse(localStorage.getItem('patents') );
    //this.socket = io.connect('http://negro/socket.io/log');
    
    /*var connection = new WebSocket('ws://localhost:8787', 'json');
    connection.onmessage = e => {
        this.information = e.data;
    };*/

    this.update();    
    setInterval(() => this.update(), 10000);
  }

  update() {
    this.currentDate = new Date();    
    //this.socket.emit('patent', {"patent":"EQF"+("0" +Math.floor(Math.random() * 999)).slice(-3),"camara":""+Math.floor((Math.random() * 4)+1), "date":new Date() , "confianza": { "1": Math.floor((Math.random() * 100)), "2": Math.floor((Math.random() * 100)), "3": Math.floor((Math.random() * 100)), "4": Math.floor((Math.random() * 100)), "5": Math.floor((Math.random() * 100)), "6": Math.floor((Math.random() * 100))} });
    this.addPatent();
  }

  addPatent() {
    var genPatent = "EQF"+("0" +Math.floor(Math.random() * 999)).slice(-3);
    var patent = {"patent": genPatent,"camera":""+Math.floor((Math.random() * 4)+1), "date":new Date() , "trust": { "1": Math.floor((Math.random() * 100)), "2": Math.floor((Math.random() * 100)), "3": Math.floor((Math.random() * 100)), "4": Math.floor((Math.random() * 100)), "5": Math.floor((Math.random() * 100)), "6": Math.floor((Math.random() * 100))} };
    var alarm = {'patent': genPatent,'alarm':""+Math.floor((Math.random() * 3)+1)}; 

    this.patents = JSON.parse(localStorage.getItem('patents') );
    if (this.patents == null) {
      this.patents = [];
    }
    this.patents.unshift(patent);
    localStorage.setItem('patents', JSON.stringify(this.patents));

    this.alarms = JSON.parse(localStorage.getItem('alarms') );
    if (this.alarms == null) {
      this.alarms = [];
    }
    this.alarms.unshift(alarm);
    localStorage.setItem('alarms', JSON.stringify(this.alarms));

  }

  showModal(src ){    
    this.showing = false;
    $( "#img1").attr( "src", src);
    this.showing = true;
  }

  closeModal(){   
    this.showing = false;
  }

  setCamera(filterCamera){
    this.filterCamera = filterCamera;
  }

  setAlarm(filterAlarm){
    this.filterAlarm = filterAlarm;
  }
}
