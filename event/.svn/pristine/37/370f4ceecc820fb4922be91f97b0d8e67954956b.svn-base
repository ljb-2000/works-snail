<!-- 事件录入组件 -->
<template>
    <div class="modal-dialog input-modal" role="document">
        <div class="modal-content">
            <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                <h4 class="modal-title" id="myModalLabel">事件录入</h4>
            </div>
            <div class="modal-body">
                <validator name="EventInputFrom">
                    <form class="form-horizontal clearfix" novalidate>
                        <div class="col-sm-5">
                            <div class="form-group">
                                <label class="col-sm-4 control-label">发生时间：</label>
                                <div class="col-sm-8">
                                    <input type="text" class="form-control">
                                </div>
                            </div>
                            <div class="form-group">
                                <label class="col-sm-4 control-label">上报时间：</label>
                                <div class="col-sm-8">
                                    <input type="text" class="form-control">
                                </div>
                            </div>
                        </div>
                        <div class="col-sm-5 col-sm-offset-1">
                            <div class="form-group">
                                <label class="col-sm-4 control-label">严重性：</label>
                                <div class="col-sm-8">
                                    <select class="form-control">
                                        <option>三级事件</option>
                                        <option>二级事件</option>
                                        <option>一级事件</option>
                                    </select>
                                </div>
                            </div>
                            <div class="form-group">
                                <label class="col-sm-4 control-label">故障类型：</label>
                                <div class="col-sm-8">
                                    <input type="text" class="form-control">
                                </div>
                            </div>
                        </div>
                        <div class="col-sm-12 input-content">
                            <label class="col-sm-2 control-label">内容：</label>
                            <div class="col-sm-9 input-txt">
                                <textarea class="form-control" v-validate:content="{ required: true }"></textarea>
                            </div>
                        </div>
                    </form>
                </validator>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-primary" :disabled="$EventInputFrom.valid ? false : true">
                    <span class="glyphicon glyphicon-ok-sign"></span>
                    提交
                </button>
                <button type="button" class="btn btn-default" data-dismiss="modal">
                    <span class="glyphicon glyphicon-remove-sign"></span>
                    关闭
                </button>
            </div>
        </div>
    </div>
</template>

<script>
    
</script>

<style scoped>
.input-modal {
    width: 800px;
    top: 50px;
}

.input-modal .modal-footer {
    text-align: center;
}

.input-content {
    margin-left: -32px;
}

.input-txt {
    width: 81%;
}
</style>