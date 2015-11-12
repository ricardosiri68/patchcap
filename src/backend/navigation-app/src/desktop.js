import {Config} from './config'; 
import {I18N} from 'aurelia-i18n';
import io from 'socket.io-client';
import {inject} from 'aurelia-framework';
import {HttpClient} from 'aurelia-fetch-client';
import 'fetch';


@inject(Config, I18N,HttpClient)
export class Desktop {
  patents;
  alarms;
  filterPatent = '';
  filterCamera = '';
  filterAlarm = '';
  config;
  showing = false;

  constructor(conf, i18n, http) {
    http.configure(config => {
      config
        .useStandardConfiguration()
        .withBaseUrl(conf.baseUri);        

    });

    this.http = http;

    this.config = conf;
    this.i18n = i18n;
    console.log(this.i18n.getLocale());

    this.socket = io('http://localhost:8084/log');                  
    //this.socket = io.connect('/log');
    this.socket.emit('register', true);

    $(window).bind("beforeunload", function() {
        this.socket.disconnect();
    });

    this.socket.on("refresh", function(deviceId, data) {
            console.log('recibiendo para '+deviceId);
            console.log(data.log);
//            $('#data').append(JSON.stringify(data.log));
    });
  
//this.socket.emit('patent', {"patent":"EQF"+("0" +Math.floor(Math.random() * 999)).slice(-3),"camara":""+Math.floor((Math.random() * 4)+1), "date":new Date() , "confianza": { "1": Math.floor((Math.random() * 100)), "2": Math.floor((Math.random() * 100)), "3": Math.floor((Math.random() * 100)), "4": Math.floor((Math.random() * 100)), "5": Math.floor((Math.random() * 100)), "6": Math.floor((Math.random() * 100))} });  

    setInterval(() => this.update(), 10000);
  }

  update() {
    this.currentDate = new Date();
    //Inserto para cargar y probar la aplicacion.    
    this.addLog();
    //this.addPatent();
    //this.activate();
    
  }

  activate(){
    this.patents= [];
    return this.http.fetch('logs', {credentials: 'include'}) 
             .then(response => response.json())      
             .then(patents => this.patents = patents)
             .catch(function(err) {
                    console.log('Fetch Error :-S', err);                
                    if(err.status == 403){
                        localStorage.removeItem("auth_token");  
                        window.location.reload();
                    }
              });
  }

addLog() {
    var genPatent = "EQF"+("0" +Math.floor(Math.random() * 999)).slice(-3);
    var date = new Date();
    var strDate = ''+date.getFullYear()+''+("0" + (date.getMonth()+1)).slice(-2)+''+ ("0" + date.getDate()).slice(-2)+''+("0" + date.getHours()).slice(-2)+''+("0" + date.getMinutes()).slice(-2)+''+("0" + date.getSeconds()).slice(-2);
    var log = {"code": genPatent,"device_id":""+Math.floor((Math.random() * 4)+1), "ts":strDate , "conf": { "1": Math.floor((Math.random() * 100)), "2": Math.floor((Math.random() * 100)), "3": Math.floor((Math.random() * 100)), "4": Math.floor((Math.random() * 100)), "5": Math.floor((Math.random() * 100)), "6": Math.floor((Math.random() * 100))} };
    console.log(log);
    this.http.fetch('logs' , { method: "POST", body: JSON.stringify(log), credentials: 'include'})
                    .catch(function(err) {  
                                            if(err.status == 403){ 
                                              localStorage.removeItem("auth_token");   
                                              window.location.reload();}
                                          });
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
