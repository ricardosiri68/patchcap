export class SelectedValueConverter {
  toView(value, array) {
  	var selected = false;
  	if(array != undefined){
	    array.forEach(
	      function (element, index, array) {	          
	        if(value == element.id){
	          selected = true;	          
	        }	        
	    });
    }
   	return selected;
  }
}