import {Config} from './config'; 
import {inject} from 'aurelia-framework';
import {HttpClient} from 'aurelia-fetch-client';
import 'fetch';

@inject(Config, HttpClient )
export class Logout{

	constructor(conf, http){
    	http.configure(config => {
      		config.useStandardConfiguration().withBaseUrl(conf.baseUri);        
    	});

    	this.http = http;    
   	}	
	

	heading = 'Login';

	activate(){
	  if(confirm('Desea Salir. Usted esta seguro? ')){
		this.http.fetch('users/logout' , { method: "POST", credentials: 'include'}) 
			.then(  
				function(response) {  
        			if (response.status !== 200) {  
            			console.log('Looks like there was a problem. Status Code: ' +  response.status);  
              			return false;  
            		}

            		
					response.json().then(function(data) {  
    					console.log(data);  
  				}); 
	        })
	        .catch(function(err) {  
              		console.log('Fetch Error :-S', err);                
        	});
	    $('#userName').text('Login').attr("href", "#/login");
	    localStorage.removeItem("user_name");  
	    localStorage.removeItem("auth_token");	    
	  }
	  window.location.href='#';
	}
}