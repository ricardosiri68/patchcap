export class StyleValueConverter {
  toView(value) {	
  	var t_class;
  	if (value < 40) {
  		t_class = 'patent-danger';
  	} else if (value < 84){
  		t_class = 'patent-warning'; //t_class = 'badge alert-success';
  	} else {
  		t_class = ''; //'badge alert-success'; //t_class = 'badge alert-warning';
  	}

   	return t_class;
  }
} 