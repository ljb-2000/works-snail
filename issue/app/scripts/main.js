var myIssue = angular.module('myIssue',["highcharts-ng","ui.bootstrap"]);

myIssue.config(['$interpolateProvider', function($interpolateProvider) {
    $interpolateProvider.startSymbol('{[');
    $interpolateProvider.endSymbol(']}');
}]);

//主页面控制器
myIssue.controller('issueCtrl', ['$scope','$uibModal','$log',function($scope,$uibModal,$log){
    var data = new Date();
    var year = data.getFullYear();
    var month = data.getMonth()-1;
    var day = data.getDay();
    $scope.datetime = year + '年' + month + '月' + day + '日';
    $scope.chart1 = {
        chart: {
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false
        },
        title: {
            text: ''
        },
        tooltip: {
            pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
        },
        plotOptions: {
            pie: {
                allowPointSelect: true,
                cursor: 'pointer',
                dataLabels: {
                    enabled: true,
                    color: '#000000',
                    connectorColor: '#000000',
                    format: '<b>{point.name}</b>: {point.percentage:.1f} %'
                }
            }
        },
        series: [{
            type: 'pie',
            name: 'Browser share',
            data: [
                ['Firefox',   45.0],
                ['IE',       26.8],
                {
                    name: 'Chrome',
                    y: 12.8,
                    sliced: true,
                    selected: true
                },
                ['Safari',    8.5],
                ['Opera',     6.2],
                ['Others',   0.7]
            ]
        }]
    };

    $scope.chart2 = {
        chart: {
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false
        },
        title: {
            text: ''
        },
        tooltip: {
            pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
        },
        plotOptions: {
            pie: {
                allowPointSelect: true,
                cursor: 'pointer',
                dataLabels: {
                    enabled: true,
                    color: '#000000',
                    connectorColor: '#000000',
                    format: '<b>{point.name}</b>: {point.percentage:.1f} %'
                }
            }
        },
        series: [{
            type: 'pie',
            name: 'Browser share',
            data: [
                ['Firefox',   45.0],
                ['IE',       26.8],
                {
                    name: 'Chrome',
                    y: 12.8,
                    sliced: true,
                    selected: true
                },
                ['Safari',    8.5],
                ['Opera',     6.2],
                ['Others',   0.7]
            ]
        }]
    };

    $scope.chart3 = {                                           
        chart: {                                                           
            type: 'bar'                                                    
        },                                                                 
        title: {                                                           
            text: ''                    
        },                                                                 
        subtitle: {                                                        
            text: 'Source: Wikipedia.org'                                  
        },                                                                                                                                 
        tooltip: {                                                         
            valueSuffix: ' millions'                                       
        },                                                                                                                                                                                                                                                                  
        series: [{
            type: 'bar',
            name: 'Browser share',
            data: [
                ['Firefox',   45.0],
                ['IE',       26.8],
                {
                    name: 'Chrome',
                    y: 12.8,
                    sliced: true,
                    selected: true
                },
                ['Safari',    8.5],
                ['Opera',     6.2],
                ['Others',   0.7]
            ]
        }]                                                                
    };

    $scope.animationsEnabled = true;

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
myIssue.controller('ModalInstanceCtrl', function ($scope, $modalInstance) {
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
  $scope.sclose='open';
  $scope.ok = function () {
    if($scope.issueInput.$valid) {
        $modalInstance.dismiss();
    }
  };

  $scope.clear = function () {
    $scope.issue.selectedId = '';
    $scope.dt = null;
    $scope.issue.sclose = 'open';
    $scope.issue.steps = 'serious';
    $scope.issue.types = 'hardware';
    $scope.issue.title = '';
    $scope.issue.description = '';
    $scope.issue.reason = '';
    $scope.issue.result = '';
  };

  //日期选择
  $scope.disabled = function(date, mode) {
    return ( mode === 'day' && ( date.getDay() === 0 || date.getDay() === 6 ) );
  };

  $scope.maxDate = new Date(2020, 5, 22);

  $scope.open = function($event) {
    $scope.status.opened = true;
  };

  $scope.dateOptions = {
    formatYear: 'yy',
    startingDay: 1
  };

  $scope.formats = ['dd-MMMM-yyyy', 'yyyy/MM/dd', 'dd.MM.yyyy', 'shortDate'];
  $scope.format = $scope.formats[0];

  $scope.status = {
    opened: false
  };

  //时间选择
  $scope.mytime = new Date();

  $scope.hstep = 1;
  $scope.mstep = 15;

  $scope.ismeridian = true;

});
