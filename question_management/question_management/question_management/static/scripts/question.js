/*--------------------------------
 * Author: luozh@snail.com
 * Date: 2015-10-26
 * Usage:
 *--------------------------------
 */

$(function(){
    //清空
    $("#i_clear").on("click",function(){
        $(".i-cx-panel").find("input").val('');
        $(".i-cx-panel").find("select option[value='']").prop("selected",true);
    });

    //====跟进表单====
    //open or close
    $(document).on("click",".m-open",function(){
        $(".close-show").removeClass('show').addClass('hide');
    });
    $(document).on("click",".m-close",function(){
        var $parents = $(this).parents("#inputModal");
        $(".close-show").removeClass('hide').addClass('show');
    });
    //清空
    /*
    $(document).on("click",".m-clear",function(){
        var $parents = $(this).parents("#inputModal");
        $parents.find("input").val('');
        $parents.find("textarea").val('');
        $parents.find(".btn-group .btn").removeClass('active');
        $parents.find("select option[value='']").prop("selected",true);
    });*/

    //提交
    $(document).on("click",".m-submit",function(){
        var $parents = $(this).parents("#inputModal");
        var question_id = $parents.find(".m-inputform").attr("data-id");
        var product = $parents.find(".m-product");
        var time = $parents.find(".modify-time");

        var status = $parents.find(".m-status .active").length;
        var level = $parents.find(".m-level .active").length;
        var type = $parents.find(".m-type .active").length;

        var title = $parents.find(".m-title");
        var describe = $parents.find(".m-describe");
        var reason = $parents.find(".m-reason");
        var result = $parents.find(".m-result");

        var title_len = getByteLen(title.val(),0);
        var describe_len = getByteLen(describe.val(),0);
        var reason_len = getByteLen(reason.val(),0);
        var result_len = getByteLen(result.val(),0);

        if($parents.find(".m-status label").eq(1).hasClass("active")) {
            if(!product.val() || !time.val() || status==0 || level==0 || type==0 || !title.val() || !describe.val() || !reason.val() || !result.val()) {
                alert("有未填写的输入项,请检查！");
                return false;
            }
        }
        else {
            if(!product.val() || !time.val() || status==0 || level==0 || type==0 || !title.val() || !describe.val()) {
                alert("有未填写的输入项,请检查！");
                return false;
            }
        }
        if(title_len>50) {
            alert("标题超过字符数限制！");
            return false;
        }
        if(describe_len>1500) {
            alert("问题描述超过字符数限制！");
            return false;
        }
        if(reason_len>1500) {
            alert("问题原因超过字符数限制！");
            return false;
        }
        if(result_len>1500) {
            alert("解决措施超过字符数限制！");
            return false;
        }

        var status_name = $parents.find(".m-status .active input").prop("name");
        var level_name = $parents.find(".m-level .active input").prop("name");
        var type_name = $parents.find(".m-type .active input").prop("name");

        $.ajax({
            url: '/question/edit/',
            type: 'POST',
            data: {
                'question_id' : question_id,
                'product_name': product.val(),
                'qtime': time.val(),
                'status': status_name,
                'level': level_name,
                'qtype': type_name,
                'title': title.val(),
                'describe': describe.val(),
                'reason': reason.val(),
                'solution': result.val()
            },
        })
        .done(function() {
            $(document).toastmessage('showSuccessToast', '跟进成功！');
            $("#inputModal").modal('hide');
            oTable_question.fnReloadAjax();
            load_charts ();
            get_summarize();
        })
        .fail(function() {
            $(document).toastmessage('showErrorToast', '跟进失败！');
        });
    });

    //检测中英文字符
    function getByteLen(val, len) {
        for (var i = 0; i < val.length; i++) {
            var a = val.charAt(i);
            if (a.match(/[^\x00-\xff]/ig) !== null) {
                len += 2;
            } else {
                len += 1;
            }
        }
        return len;
    }

    //查询表格刷新功能
    $.fn.dataTableExt.oApi.fnReloadAjax = function(oSettings, sNewSource, fnCallback, bStandingRedraw) {
        if (typeof sNewSource != 'undefined' && sNewSource != null) {
            oSettings.sAjaxSource = sNewSource;
        }

        // Server-side processing should just call fnDraw
        if (oSettings.oFeatures.bServerSide) {
            this.fnDraw();
            return;
        }

        this.oApi._fnProcessingDisplay(oSettings, true);
        var that = this;
        var iStart = oSettings._iDisplayStart;
        var aData = [];

        this.oApi._fnServerParams(oSettings, aData);

        oSettings.fnServerData.call(oSettings.oInstance, oSettings.sAjaxSource, aData, function(json) {
            that.oApi._fnClearTable(oSettings);
            var aData = (oSettings.sAjaxDataProp !== "") ?
                that.oApi._fnGetObjectDataFn(oSettings.sAjaxDataProp)(json) : json;

            for (var i = 0; i < aData.length; i++) {
                that.oApi._fnAddData(oSettings, aData[i]);
            }

            oSettings.aiDisplay = oSettings.aiDisplayMaster.slice();

            if (typeof bStandingRedraw != 'undefined' && bStandingRedraw === true) {
                oSettings._iDisplayStart = iStart;
                that.fnDraw(false);
            } else {
                that.fnDraw();
            }

            that.oApi._fnProcessingDisplay(oSettings, false);

            
            if (typeof fnCallback == 'function' && fnCallback != null) {
                fnCallback(oSettings);
            }
        }, oSettings);
    }

    //查询
    $("#i_fliter").on("click",function(){
        var product_id = $("#i_product").val();
        var qtime_from = $("#i_findtime_form").val();
        var qtime_to = $("#i_findtime_to").val();
        var level = $("#i_level").val();
        var create_user = $("#i_name").val();
        var created_from = $("#i_inputtime_form").val();
        var created_to = $("#i_inputtime_to").val();
        var describe = $("#i_description").val();
        var status = $("#i_status").val();
        var qtype = $("#i_type").val();
        var title = $("#i_title").val();

        oTable_question.fnReloadAjax('/question/list/?p=0&product_id=' + product_id + '&qtime_from=' + qtime_from + '&qtime_to=' + qtime_to + '&level=' + level + '&create_user=' + create_user + '&created_from=' + created_from + '&created_to=' + created_to + '&describe=' + describe + '&status=' + status + '&qtype=' + qtype+ '&title=' + title);
    });
});

//绘图
load_charts ();
function load_charts () {
    //chart1
    $.ajax({
        type: 'GET',
        url: '/question/ajax_get_type_num/',
        dataType: 'json',
        success: function(msg) {
            if (msg.result == 1) {
                $('#container1').highcharts({
                    chart: {
                        plotBackgroundColor: null,
                        plotBorderWidth: null,
                        plotShadow: false
                    },
                    title: {
                        text: ''
                    },
                    tooltip: {
                        pointFormat: '比例：<b>{point.percentage:.2f}%</b>'
                    },
                    plotOptions: {
                        pie: {
                            allowPointSelect: true,
                            cursor: 'pointer',
                            dataLabels: {
                                enabled: true,
                                color: '#000000',
                                connectorColor: '#000000',
                                format: '<b>{point.name}</b>: {point.y}'
                            }
                        }
                    },
                    series: [{
                        type: 'pie',
                        name: '',
                        data: msg.data
                    }]
                });
            }
        },
        error: function() {
        }
    });
    
    //chart2
    $.ajax({
        type: 'GET',
        url: '/question/ajax_get_level_num/',
        dataType: 'json',
        success: function(msg) {
            if (msg.result == 1) {
                $('#container2').highcharts({
                    chart: {
                        plotBackgroundColor: null,
                        plotBorderWidth: null,
                        plotShadow: false,
                    },
                    title: {
                        text: ''
                    },
                    tooltip: {
                        pointFormat: '比例：<b>{point.percentage:.2f}%</b>'
                    },
                    plotOptions: {
                        pie: {
                            allowPointSelect: true,
                            cursor: 'pointer',
                            dataLabels: {
                                enabled: true,
                                color: '#000000',
                                connectorColor: '#000000',
                                format: '<b>{point.name}</b>: {point.y}'
                            }
                        }
                    },
                    series: [{
                        type: 'pie',
                        name: '',
                        data: msg.data
                    }]
                });
            }
        },
        error: function() {
        }
    });
    
    //chart3
    $.ajax({
        type: 'GET',
        url: '/question/ajax_get_product_num/',
        dataType: 'json',
        success: function(msg) {
            if (msg.result == 1) {
                var product_info_list = msg.data;
                var product_name_list = [];
                var product_num_list = [];
                for(i=0;i<product_info_list.length;i++){
                    var product_info = product_info_list[i];
                    product_name_list.push(product_info[1]);
                    product_num_list.push(product_info[0]);
                } 
                $('#container3').highcharts({                              
                    chart: {                                                           
                        type: 'bar'                                                    
                    },                                                                 
                    title: {                                                           
                        text: ''                    
                    },                                                                 
                    xAxis: {                                                           
                        categories: product_name_list,
                        title: {                                                       
                            text: ''                                                 
                        }                                                              
                    },                                                                 
                    yAxis: {                                                           
                        min: 0,
                        allowDecimals: false,                                                     
                        title: {                                                       
                            text: '',                             
                        },                                                             
                        labels: {                                                      
                            overflow: 'justify'                                        
                        }                                                              
                    },                                                                 
                    tooltip: {     
                        pointFormat: '数量：<b>{point.y}</b>',
                        valueSuffix: ' 个'                                       
                    },                                                                 
                    plotOptions: {                                                     
                        bar: {                                                         
                            dataLabels: {
                                enabled: true                                          
                            }                                                          
                        }                                                              
                    },                                                                 
                    legend: {
                        enabled: false
                    },                                                            
                    series: [{                                                         
                        data: product_num_list                                   
                    },]                                                                 
                });
            }
        },
        error: function() {
        }
    });
};

//获取统计数据
function get_summarize() {
    $.ajax({
        url: '/question/ajax_get_summarize/',
        type: 'GET',
        dataType:'json'
    })
    .done(function(data) {
        $(".i-nav .user").html(data.username);
        $(".i-nav .datetime").html(data.year+'年'+data.month+'月'+data.day+'日');
        $(".i-nav .red").html(data.total);
        $(".i-nav .blue").html(data.open_num);
        $(".i-nav .green").html(data.close_num);
    })
    .fail(function() {
        $(document).toastmessage('showErrorToast', '获取统计信息失败！');
    });  
}

//跟进弹框
function question_edit(question_id){
    $.ajax({
        type: 'get',
        url: '/question/edit/',
        data: {
            'question_id': question_id,
        },
        dataType: 'json',
        success: function(data) {
            if (data.status == 200) {
                $('#inputModal').html(data.html);
                $('#inputModal').modal('show');
            }
        },
        error: function(re, status) {}
    });
    return false;
}

//查看弹框
function question_view(question_id){
    $.ajax({
        type: 'get',
        url: '/question/view/',
        data: {
            'question_id': question_id,
        },
        dataType: 'json',
        success: function(data) {
            if (data.status == 200) {
                $('#inputModal').html(data.html);
                $('#inputModal').modal('show');
            }
        },
        error: function(re, status) {}
    });
    return false;
}

//时间选择控件
$("#i_findtime_form,#i_findtime_to,#i_inputtime_form,#i_inputtime_to").datetimepicker({
    timeFormat: "HH:mm",
    dateFormat: "yy-mm-dd"
});

//模糊匹配
$("#i_title").autocomplete({
    source:function( request, response ) {
        $.ajax({
            type:"GET",
            url: "/question/ajax_get_question_title/",
            dataType: "json",
            data:{'title':request.term},
            success: function( data ) {
                var arr = data.title_list;
                response( $.map( arr, function(item) {
                    return item;
                }));
            }
        });
    }
});
$("#i_description").autocomplete({
    source:function( request, response ) {
        $.ajax({
            type:"GET",
            url: "/question/ajax_get_question_describe/",
            dataType: "json",
            data:{'describe':request.term},
            success: function( data ) {
                var arr = data.describe_list;
                response( $.map( arr, function(item) {
                    return item;
                }));
            }
        });
    }
});

//datatable
var oTable_question = null;
$(document).ready(function() {
    oTable_question = $('#question_table').dataTable({
         "sDom": 'lfrtip',
         "bLengthChange":false,
         "iDisplayLength":10,
         "aoColumnDefs": [{ "bSortable": false, "aTargets": [9] }],
         "aaSorting": [[ 8, "desc" ]],
         "bProcessing": true,
         "bServerSide": true,
         "sPaginationType": "full_numbers",
         "sAjaxSource": "/question/list/",
         "bFilter":false,
         "oLanguage":{
               "sUrl":'/static/scripts/data_table/cn/jquery.dataTable.cn.txt'
          }
     });
});