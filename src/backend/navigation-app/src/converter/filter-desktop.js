export class FilterValueConverter {
  toView(array, filterCamera, filterAlarm, filterPatent, alarms) {	    
    
  return array.filter( function (elem) {
   		var date = new Date(elem.date);
   		elem.picture = './images/'+elem.camera+'/'+date.getFullYear()+''+("0" + (date.getMonth()+1)).slice(-2)+''+ ("0" + date.getDate()).slice(-2)
    			+''+("0" + date.getHours()).slice(-2)+''+("0" + date.getMinutes()).slice(-2)+''+("0" + date.getSeconds()).slice(-2)+'.jpg';

      //elem.alarma = 3;//alarmaTipo;
      
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
   				&& (filterPatent == '' || elem.patent.indexOf(filterPatent)>=0)
          && (filterAlarm == '' || elem.alarmType.indexOf(filterAlarm)>=0);
   	});   
  }
} 
