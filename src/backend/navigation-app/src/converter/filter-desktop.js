export class FilterValueConverter {
  toView(array, filterCamera, filterAlarm, filterPatent, alarms) {	    
    
  return array.filter( function (elem) {
   		var date = new Date(elem.ts);
   		elem.picture = './images/'+elem.camera+'/'+date.getFullYear()+''+("0" + (date.getMonth()+1)).slice(-2)+''+ ("0" + date.getDate()).slice(-2)
    			+''+("0" + date.getHours()).slice(-2)+''+("0" + date.getMinutes()).slice(-2)+''+("0" + date.getSeconds()).slice(-2)+'.jpg';

      elem.camera = elem.device_id; //TODO Deberia traducir el id de la camara y ponerle el nombre
      elem.trust = elem.conf.split(",");
      
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
   				&& (filterPatent == '' || elem.code.indexOf(filterPatent)>=0)
          && (filterAlarm == '' || elem.alarmType.indexOf(filterAlarm)>=0);
   	});   
  }
} 
