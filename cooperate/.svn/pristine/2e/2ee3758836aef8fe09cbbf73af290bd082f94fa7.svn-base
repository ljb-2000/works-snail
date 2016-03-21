/**
 * 
 * @authors luozh@snail.com
 * @date    2016-01-19 09:45:35
 * @version weekly.html
 */

// datetime
$('.datetime-from, .datetime-to, .weektime-to, .weektime-from').datetimepicker({
    weekStart: 1,
    /*endDate: '2016-01-20',*/
    todayBtn: 1,
    autoclose: 1,
    todayHighlight: 1,
    startView: 2,
    minView: 2,
    forceParse: 0,
    linkField: "mirror_field",
    pickerPosition: "bottom-left"
});

// Vue对象
var vm = new Vue({
    el: '#week_box',
    data: {
        curSelected: '',
        curDepartment: '',
        departments: [],
        startTime: '',
        endTime: '',
        searchStart: '',
        searchEnd: '',
        weekList: [],
        progressValue: '',
        planValue: '',
        progressGroup: [],
        planGroup: [],
        weeklyId: ''
    },
    methods: {

        // 初次加载渲染
        getList: function(departmentName) {
            $.ajax({
                url: '/report/ajax_get_weeklys/',
                type: 'POST',
                dataType: 'json',
                data: {
                    department_name: departmentName,
                    start_time: vm.searchStart,
                    end_time: vm.searchEnd
                }
            })
            .done(function(data) {
                vm.weekList = data.list;
                vm.departments = data.department;
                vm.curDepartment = vm.departments[0];

                vm.curSelected === '' ? vm.curSelected = vm.departments[0] : '';
                vm.searchStart === '' ? vm.searchStart = data.start_time : '';
                vm.searchEnd === '' ? vm.searchEnd = data.end_time : '';
                vm.startTime === '' ? vm.startTime = data.start_time : '';
                vm.endTime === '' ? vm.endTime = data.end_time : '';
            })
            .fail(function() {
                showAlert('jError', '出错了 :(', false);
            });
        },

        // 编辑周报
        editFn: function(index) {
            var list = this.weekList[index],
                progress = list.progress,
                plan = list.plan,
                progressLen = progress.length,
                planLen = plan.length,
                i,
                j;

            this.weeklyId = list.id;
            this.progressValue = progress[0];
            this.planValue = plan[0];
            this.curDepartment = this.curSelected;
            vm.progressGroup = [];
            vm.planGroup = [];

            for (i = 1; i < progressLen; i++) {
                vm.progressGroup.push({
                    value: progress[i]
                });
            }

            for (j = 1; j < planLen; j++) {
                vm.planGroup.push({
                    value: plan[j]
                });
            }
            
            $('#my_tab a[href="#tab_two"]').tab('show');
        },

        // 删除周报
        deleteFn: function(index) {
            var isDelete = confirm('是否确认删除？');

            if (isDelete) {
                $.ajax({
                    url: '/report/ajax_delete_weekly/',
                    type: 'POST',
                    dataType: 'json',
                    data: {
                        id: vm.weekList[index].id
                    }
                })
                .done(function(data) {
                    if (data.result === 1) {
                        vm.weekList.splice(index, 1);

                        showAlert('jSuccess', '删除成功 :)', true);
                    } else {
                        showAlert('jError', '删除失败 :(', false);
                    }
                })
                .fail(function() {
                    showAlert('jError', '删除失败 :(', false);
                });
            }
        },

        // 取消编辑
        cancelEdit: function() {
            this.weeklyId = '';
            this.progressValue = '';
            this.planValue = '';
            this.progressGroup = [];
            this.planGroup = [];
        },

        // 添加工作进展
        addProgress: function() {
            this.progressGroup.push({
                value: ''
            });
        },

        // 删除工作进展
        removeProgress: function(index) {
            this.progressGroup.splice(index, 1);
        },

        // 添加工作计划
        addPlan: function() {
            this.planGroup.push({
                value: ''
            });
        },

        // 删除工作计划
        removePlan: function(index) {
            this.planGroup.splice(index, 1);
        },

        // 确认提交
        comfirm: function() {
            var progressArr = this.progressGroup,
                planArr = this.planGroup,
                progressData = [],
                planData = [];

            this.progressValue.trim() !== '' ? progressData.push(this.progressValue) : '';
            this.planValue.trim() !== '' ? planData.push(this.planValue) : '';

            progressArr.forEach(function(e) {
                if (e.value.trim() !== '') {
                    progressData.push(e.value);
                }
            });

            planArr.forEach(function(e) {
                if (e.value.trim() !== '') {
                    planData.push(e.value);
                }
            });

            if (progressData.length && planData.length && this.startTime && this.endTime) {

                // DOTO AJAX
                $.ajax({
                    url: '/report/ajax_edit_weekly/',
                    type: 'POST',
                    dataType: 'json',
                    data: {
                        id: vm.weeklyId,
                        department_name: vm.curDepartment,
                        start_time: vm.startTime,
                        end_time: vm.endTime,
                        progress_list: progressData,
                        plan_list: planData
                    }
                })
                .done(function(data) {
                    if (data.result === 1) {
                        vm.progressGroup = [];
                        vm.planGroup = [];
                        vm.progressValue = '';
                        vm.planValue = '';

                        vm.getList(vm.curSelected);

                        showAlert('jSuccess', '提交成功 :)', true);
                    } else {
                        showAlert('jError', '出错了 :(', false);
                    }
                })
                .fail(function() {
                    showAlert('jError', '出错了 :(', false);
                });
            } else {
                showAlert('jNotify', '有尚未填写的输入项，请检查 :(', true);
            }
        }
    }
});

// 渲染周报列表
vm.getList('');
