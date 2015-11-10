export class alertPatentValueConverter {
  toView(value) {
    var values = value.split('|');
  	var t_class;  	
    switch(values[0]) {
      case '1':
        t_class = 'alert-patent-tipo-1';
        break;
      case '2':
        t_class = 'alert-patent-tipo-2';
        break;
      default:
        t_class = 'alert-patent-default';
    }

   	return t_class;
  } 
}