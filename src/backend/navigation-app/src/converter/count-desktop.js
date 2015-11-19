export class CountValueConverter {
  toView(array, filterCamera, filterAlarm, alarms) {	  	
   	return array.filter( function (elem) {

    elem.camera = elem.device_id; //TODO Deberia traducir el id de la camara y ponerle el nombre

 	  var alarmType= '';
      (alarms.filter( function (elemento) { return elemento.plate.indexOf(elem.code)>=0})).forEach(
      function (element, index, array) {          
        if(alarmType == '')
          alarmType = ''+element.alarm;
        else
          alarmType += '|'+element.alarm;
        });
      
       elem.alarmType = alarmType;

   		return (elem.camera == filterCamera || filterCamera == '') 
   				&& (filterAlarm == '' || elem.alarmType.indexOf(filterAlarm)>=0);
   				
   	}).length;   
  }
} 
