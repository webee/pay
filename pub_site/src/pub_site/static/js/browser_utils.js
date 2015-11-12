var is_chrome = navigator.userAgent.indexOf('Chrome') > -1;
var is_explorer = navigator.userAgent.indexOf('MSIE') > -1;
var is_firefox = navigator.userAgent.indexOf('Firefox') > -1;
var is_safari = navigator.userAgent.indexOf("Safari") > -1;
var is_opera = navigator.userAgent.toLowerCase().indexOf("op") > -1;
if ((is_chrome)&&(is_safari)) {is_safari=false;}
if ((is_chrome)&&(is_opera)) {is_chrome=false;}


function navigateToUrl(url) {
    var f = document.createElement("FORM");
    f.action = url;

    var indexQM = url.indexOf("?");
    if (indexQM>=0) {
        // the URL has parameters => convert them to hidden form inputs
        var params = url.substring(indexQM+1).split("&");
        for (var i=0; i<params.length; i++) {
            var keyValuePair = params[i].split("=");
            var input = document.createElement("INPUT");
            input.type="hidden";
            input.name  = keyValuePair[0];
            input.value = keyValuePair[1];
            f.appendChild(input);
        }
    }

    document.body.appendChild(f);
    f.submit();
}
