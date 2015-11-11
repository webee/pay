
function getUrlArgObject(){ 
    var args=new Object(); 
    var query=location.search.substring(1);//获取查询串 
    var pairs=query.split(",");//在逗号处断开 
    for(var i=0;i<pairs.length;i++){ 
        var pos=pairs[i].indexOf('=');//查找name=value 
        if(pos==-1){//如果没有找到就跳过 
            continue; 
        } 
        var argname=pairs[i].substring(0,pos);//提取name 
        var value=pairs[i].substring(pos+1);//提取value 
        args[argname]=unescape(value);//存为属性 
    } 
    return args;//返回对象 
} 

var urlparams = getUrlArgObject();

app.controller('searchCtrl',['$scope','$http','absUrl', function($scope, $http, absUrl) {
		var orderid=urlparams["orderid"];
	    $http.get(absUrl("/recon/gettx/"+orderid))
		    .success(function(response) {
				$scope.tx = response.tx;
				}).error(function(){
				});
		$scope.toggle = function (txid) {
	    	$http.get(absUrl("/recon/gettxdetail/"+txid))
		    .success(function(response) {
				$scope.txd = response.txdetail;
				$scope.ad = response.ad;
				}).error(function(){
				});
			
		};
}]);

