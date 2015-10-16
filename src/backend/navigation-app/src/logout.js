import {Configuration} from './configuration'; 
import {inject} from 'aurelia-framework';
import {HttpClient} from 'aurelia-fetch-client';
import 'fetch';

@inject(Configuration, HttpClient )
export class Logout{

	constructor(conf, http){
    	http.configure(config => {
      		config.useStandardConfiguration().withBaseUrl(conf.baseUri);        
    	});

    	this.http = http;    
   	}	
	

	heading = 'Login';

	activate(){
		this.http.fetch('users/logout' , { method: "POST"}) //, credentials: 'include'
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
	    $('#userName').text('Login');
	    localStorage.removeItem("auth_token");


	    window.location.href='#';
	}
}