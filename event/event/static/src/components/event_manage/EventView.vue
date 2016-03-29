<!-- 事件查看组件 -->
<template>
    <div class="modal-dialog view-modal" role="document">
        <div class="modal-content">
            <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                <h4 class="modal-title" id="myModalLabel">事件查看</h4>
            </div>
            <div class="modal-body">
                <form class="form-horizontal clearfix">
                    <div class="col-sm-5">
                        <div class="form-group">
                            <label class="col-sm-4 control-label">发生时间：</label>
                            <div class="col-sm-8">
                                <input type="text" class="form-control" value="2016-03-22 20:24">
                            </div>
                        </div>
                        <div class="form-group">
                            <label class="col-sm-4 control-label">上报时间：</label>
                            <div class="col-sm-8">
                                <input type="text" class="form-control" value="2016-03-22 20:30">
                            </div>
                        </div>
                    </div>
                    <div class="col-sm-5 col-sm-offset-1">
                        <div class="form-group">
                            <label class="col-sm-4 control-label">严重性：</label>
                            <div class="col-sm-8">
                                <select class="form-control">
                                    <option>三级事件</option>
                                    <option selected>二级事件</option>
                                    <option>一级事件</option>
                                </select>
                            </div>
                        </div>
                        <div class="form-group">
                            <label class="col-sm-4 control-label">故障类型：</label>
                            <div class="col-sm-8">
                                <input type="text" class="form-control" value="人为故障">
                            </div>
                        </div>
                    </div>
                    <div class="col-sm-12 view-content">
                        <label class="col-sm-2 control-label">内容：</label>
                        <div class="col-sm-9 view-txt">
                            <textarea class="form-control">很多玩家反应太极熊猫在线充值无法到账</textarea>
                        </div>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-success">
                    <span class="glyphicon glyphicon-ok-sign"></span>
                    保存
                </button>
                <button type="button" class="btn btn-primary">
                    <span class="glyphicon glyphicon-edit"></span>
                    修改
                </button>
                <button type="button" class="btn btn-warning">
                    <span class="glyphicon glyphicon-remove-sign"></span>
                    关闭
                </button>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    events: {
        'child-msg': function (msg) {
            console.log(msg);
        }
    }
}
</script>

<style scoped>
.view-modal {
    width: 800px;
    top: 50px;
}

.view-modal .modal-footer {
    text-align: center;
}

.view-content {
    margin-left: -32px;
}

.view-txt {
    width: 81%;
}
</style>