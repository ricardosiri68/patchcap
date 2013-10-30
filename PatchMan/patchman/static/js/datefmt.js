function DateFmt(fstr) {
  this.formatString = fstr

  var mthNames = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  var dayNames = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];
  var zeroPad = function(number) {
     return ("0"+number).substr(-2,2);
  }

  var dateMarkers = {
    d:['getDate',function(v) { return zeroPad(v)}],
    m:['getMonth',function(v) { return zeroPad(v+1)}],
    n:['getMonth',function(v) { return mthNames[v]; }],
    w:['getDay',function(v) { return dayNames[v]; }],
    y:['getFullYear'],
    H:['getHours',function(v) { return zeroPad(v)}],
    M:['getMinutes',function(v) { return zeroPad(v)}],
    S:['getSeconds',function(v) { return zeroPad(v)}],
    i:['toISOString']
  };

  this.format = function(date) {
    var dateTxt = this.formatString.replace(/%(.)/g, function(m, p) {
      var rv = date[(dateMarkers[p])[0]]()

      if ( dateMarkers[p][1] != null ) rv = dateMarkers[p][1](rv)

      return rv

    });

    return dateTxt
  }

}
