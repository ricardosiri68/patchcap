export class CountValueConverter {
  toView(array, filterCamera, filterAlarm, alarms) {	  	
   	return array.filter( function (elem) {

 	  var alarmType= '';
      (alarms.filter( function (elemento) { return elemento.patent.indexOf(elem.patent)>=0})).forEach(
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
