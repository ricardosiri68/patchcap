export class SelectedValueConverter {
  toView(value, array) {
	console.log("value:",value);
  	var selected = false;
  	if(array != undefined){
	    array.forEach(
	      function (element, index, array) {	          
	        if(value == element.id){
	          selected = true;	          
	        }	        
	    });
    }
    console.log("selected:",selected);
   	return selected;
  }
}