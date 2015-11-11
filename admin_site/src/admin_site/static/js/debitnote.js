var app = angular.module('debitnote', ['global-config']).config(function ($interpolateProvider) {
        $interpolateProvider.startSymbol('[[');
        $interpolateProvider.endSymbol(']]');
    }) 
angular.module('debitnote').service('absUrl', ["globalConfig", function(globalConfig){
	    return function(suffix) {
			        return globalConfig.apiHost + suffix;
				}
}]);
