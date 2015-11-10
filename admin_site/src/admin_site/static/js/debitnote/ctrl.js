app.controller('debitnoteCtrl',['$scope','$http','absUrl', function($scope, $http, absUrl) {
	    $http.get(absUrl("/recon/getrecondata"))
		    .success(function(response) {
				$scope.datestr = response.date;
				$scope.datas = response.data;
				$scope.num = response.num;
				}).error(function(){
					 alert("an unexpected error ocurred!");
				});
}]);

