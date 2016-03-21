/**
 * 
 * @authors luozh@snail.com
 * @date    2016-01-19 09:45:35
 * @version upload.html
 */

var vm = new Vue({
    el: '#upload_box',
    data: {
        searchDoc: '',
        docs: [],
        docPath: '',
        len: '10',
        user: ''
    },
    methods: {

        // 初始加载
        getDocs: function(length) {
            $.ajax({
                    url: '/input/ajax_get_files/',
                    type: 'POST',
                    dataType: 'json',
                    data: {
                        length: vm.len
                    }
                })
                .done(function(data) {
                    vm.docs = data;
                })
                .fail(function() {
                    showAlert('jError', '出错了 :(', false);
                });
        },

        // 搜索文件
        searchFn: function() {
            $.ajax({
                    url: '/input/ajax_get_files/',
                    type: 'POST',
                    dataType: 'json',
                    data: { 
                        textstr: vm.searchDoc 
                    }
                })
                .done(function(data) {
                    vm.docs = data;
                })
                .fail(function() {
                    showAlert('jError', '出错了 :(', false);
                });
        },

        // 选择文件
        selectDocs: function() {
            $('#upload_file').trigger('click');
        },

        // 获取路径
        getPath: function() {
            this.docPath = $('#upload_file').val();
        },

        // 文件上传
        uploadFile: function() {
            var formData = new FormData($('#file_form')[0]),
                path = this.docPath;

            if (this.docPath === '') {
                showAlert('jNotify', '请先选择上传文件！', true);

                return false;
            }

            $.ajax({
                    url: '/input/ajax_upload_file/',
                    type: 'POST',
                    processData: false,
                    contentType: false,
                    dataType: 'JSON',
                    data: formData
                })
                .done(function(data) {
                    if (data.result === 1) {
                        showAlert('jSuccess', '文件上传成功 :)', true);

                        vm.docPath = '';

                        vm.getDocs();
                    } else {
                        showAlert('jError', '文件上传失败 :(', false);
                    }
                })
                .fail(function() {
                    showAlert('jError', '文件上传失败 :(', false);
                });
        },

        // 删除文件
        deleteFn: function(index) {
            var obj = vm.docs[index];

            if (obj.del === true) {
                var isDelete = confirm('是否确认删除？');

                if (isDelete) {
                    $.ajax({
                        url: '/input/ajax_delete_file/',
                        type: 'POST',
                        dataType: 'json',
                        data: {
                            id: obj.id
                        }
                    })
                    .done(function(data) {
                        if (data.result === 1) {
                            vm.docs.splice(index, 1);

                            showAlert('jSuccess', '删除成功 :)', true);
                        } else {
                            showAlert('jError', '删除失败 :(', false);
                        }
                    })
                    .fail(function() {
                        showAlert('jError', '删除失败 :(', false);
                    });
                }
            } else {
                showAlert('jNotify', '无权限操作 :(', true);
            }
        }
    }
});

// 渲染文件列表
vm.getDocs('10');
