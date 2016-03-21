var myIssue = angular.module('myIssue',["ui.bootstrap"]);

myIssue.config(['$interpolateProvider', function($interpolateProvider) {
    $interpolateProvider.startSymbol('{[');
    $interpolateProvider.endSymbol(']}');
}]);

/* 路由功能
myIssue.config(['$routeProvider',function ($routeProvider) {  
    $routeProvider  
        .when('/index/input', {  
            templateUrl: 'model.html',  
        })   
        .otherwise({  
            redirectTo: '/index'  
        });  
}]); */

//主页面控制器
myIssue.controller('issueCtrl', ['$scope','$uibModal','$log',function($scope,$uibModal,$log){
    $scope.animationsEnabled = true;
    //录入
    $scope.open = function (size) {
        var modalInstance = $uibModal.open({
          animation: $scope.animationsEnabled,
          templateUrl: 'myModalContent.html',
          controller: 'ModalInstanceCtrl',
          size: size
        });
    };
}]);


// 问题录入控制器
myIssue.controller('ModalInstanceCtrl', ['$scope','$modalInstance','$http',function($scope, $modalInstance, $http) {
    var transform = function(data){
        return $.param(data);
    };
    $("#time").datetimepicker({
        timeFormat: "HH:mm",
        dateFormat: "yy-mm-dd"
    });
    $scope.radioStatus = '0';
    $scope.products = [
        {
            'id':'001',
            'name':'关云长'
        },
        {
            'id':'002',
            'name':'太极熊猫'
        }
    ]
    $scope.sclose='0';
    $scope.hclose = function(){
        $modalInstance.dismiss();
    }
    $scope.ok = function () {
        var date = $scope.dt;
        var year = date.getFullYear();
        var month = date.getMonth() + 1;
        var day = date.getDate();
        var time = $scope.mytime;
        var hour = time.getHours();
        var min = time.getMinutes();
        var dt = year + "-" + month + "-" + day + " " + hour + ":" + min;
        if($scope.issueInput.$valid) {
            $http({
                    method:"POST",
                    url:"/question/add/",
                    data: {
                        'product_name': $scope.issue.selectedId,
                        'qtime': dt,
                        'status': $scope.radioStatus,
                        'level': $scope.radioSteps,
                        'qtype': $scope.radioTypes,
                        'title': $scope.issue.title,
                        'describe': $scope.issue.description,
                        'reason': $scope.issue.reason,
                        'solution': $scope.issue.result
                    },
                    headers: {'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'},
                    transformRequest: transform
                }).success(function(data){
                    $(document).toastmessage('showSuccessToast', '录入成功！');
                    $modalInstance.dismiss();
                    load_charts ();
                    oTable_question.fnReloadAjax();
                    get_summarize();
                }).error(function(){
                    $(document).toastmessage('showErrorToast', '录入失败！');
                });
        }
    };

  $scope.clear = function () {
    $scope.issue.selectedId = '';
    $scope.dt = new Date();
    $scope.radioStatus = '0';
    $scope.radioSteps = null;
    $scope.radioTypes = null;
    $scope.issue.title = '';
    $scope.issue.description = '';
    $scope.issue.reason = '';
    $scope.issue.result = '';
    $scope.mytime = new Date();
  };

  //日期选择
  $scope.dt = new Date();
  $scope.maxDate = new Date(2020, 5, 22);

  $scope.opendate = function($event) {
    $scope.status.opened = true;
  };

  $scope.dateOptions = {
    formatYear: 'yy',
    startingDay: 1
  };

  $scope.format = 'yyyy-MM-dd';

  $scope.status = {
    opened: false
  };

  //时间选择
  $scope.mytime = new Date();

  $scope.hstep = 1;
  $scope.mstep = 1;

  $scope.ismeridian = true;

}]);

