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
            });
	}
}