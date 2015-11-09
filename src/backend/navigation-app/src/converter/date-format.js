export class DateFormatValueConverter {
  toView(value) {
  	var date = new Date(value);
    return date.toLocaleString();
  }
}