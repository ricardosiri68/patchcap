import {Config} from './config'; 
import {inject} from 'aurelia-framework';
import {HttpClient} from 'aurelia-fetch-client';
import 'fetch';


@inject(Config, HttpClient )
export class Login{

	constructor(conf, http){
    	http.configure(config => {
      		config.useStandardConfiguration().withBaseUrl(conf.baseUri);        
    	});

    	this.http = http;    
   	}	
	

	heading = 'Login';
	
	username='';
	password='';
	login(){
		var there = this;
		this.http.fetch('users/login' , { method: "POST",
									    	body: JSON.stringify({username: this.username,password: this.password}),
											credentials: 'include'})
			.then(  
				function(response) {  
            		if (response.status !== 200) {  
                		console.log('Looks like there was a problem. Status Code: ' +  response.status);  
                  		return false;  
                	}

              	localStorage.setItem("auth_token", "ah12h3");              	

              	there.http.fetch('users/me' , { method: "POST" , credentials: 'include'}) 
        				.then(  
        					function(response) {  
                    			if (response.status !== 200) {  
                        			console.log('Looks like there was a problem. Status Code: ' +  response.status);  
                          			return false;  
                        		}

        						response.json().then(function(data) {  
                					console.log(data);  
        			           	  	$('#userName').text(data.name).attr("href", "#/logout");
                              localStorage.setItem("user_name", data.name);               

              				});                      	
        	    
  	            })
  	            .catch(function(err) {  
                		console.log('Fetch Error :-S', err);    

              	});
   	          	window.location.href='#';

        })  
        .catch(function(err) {  
          console.log('Fetch Error :-S', err);                
          if (err.status == 400) {  
            //Usuario Requerido
            err.json().then(function(data) { 
                var mensaje = '';
                if (data.username != undefined && data.username == 'Required'){
                  mensaje += 'Username Requerido \n';
                }
                if (data.password != undefined && data.password == 'Required'){
                  mensaje += 'Password Requerido';
                }
                $('#alert-login').html('<div class="alert alert-danger" role="alert"> <span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true"></span> <span class="sr-only">Error:</span>'+mensaje+'</div>');
            });
           
          } else if (err.status == 401) {  
            //Usuario No Autorizado
            $('#alert-login').html('<div class="alert alert-danger" role="alert"> <span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true"></span> <span class="sr-only">Error:</span> Usuario No autorizado</div>');
          }
        });
	}
}