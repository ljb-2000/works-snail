<!-- 历史事件组件 -->
<template>
    <div class="right-wrap">
        <div class="row">
            <div class="col-sm-12">
                <div class="right-header">
                    <div class="pull-left">
                        <h5>事件查询</h5>
                    </div>
                </div>
                <div class="right-body">
                    <form class="form-inline">
                        <div class="form-group">
                            <label class="control-label">事件ID：</label>
                            <input type="text" class="form-control">
                        </div>
                        <div class="form-group">
                            <label class="control-label">业务属性：</label>
                            <select class="form-control">
                                <option>全部</option>
                                <option>太极熊猫</option>
                                <option>关云长</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="control-label">事件级别：</label>
                            <select class="form-control">
                                <option>全部</option>
                                <option>一级事件</option>
                                <option>二级事件</option>
                                <option>三级事件</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="control-label">处理状态：</label>
                            <select class="form-control">
                                <option>全部</option>
                                <option>未处理</option>
                                <option>已处理</option>
                                <option>正在处理</option>
                            </select>
                        </div>
                        <div class="form-group pull-right">
                            <button type="button" class="btn btn-default">
                                <span class="glyphicon glyphicon-search"></span>
                                查询
                            </button>
                            <button type="button" class="btn btn-default">
                                <span class="glyphicon glyphicon-repeat"></span>
                                重置
                            </button>
                        </div>
                    </form>
                    <table class="mt30 table table-hover table-bordered table-striped">
                        <thead>
                            <tr>
                                <td>事件ID</td>
                                <td>所属业务</td>
                                <td>事件内容</td>
                                <td>事件级别</td>
                                <td>处理状态</td>
                                <td>操作</td>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>01</td>
                                <td>关云长</td>
                                <td>酒仙桥机房丢包严重</td>
                                <td>三级事件</td>
                                <td>已处理</td>
                                <td>
                                    <span class="event-view" @click="viewEvent" data-toggle="modal" data-target="#event_view">查看</span>
                                </td>
                            </tr>
                            <tr>
                                <td>02</td>
                                <td>太极熊猫</td>
                                <td>充值队列卡死</td>
                                <td>三级事件</td>
                                <td>已处理</td>
                                <td>
                                    <span class="event-view" data-toggle="modal" data-target="#event_view">查看</span>
                                </td>
                            </tr>
                            <tr>
                                <td>03</td>
                                <td>天子</td>
                                <td>在线人数异常</td>
                                <td>一级事件</td>
                                <td>已处理</td>
                                <td>
                                    <span class="event-view" data-toggle="modal" data-target="#event_view">查看</span>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <div class="modal fade" id="event_view" tabindex="-1" role="dialog">
        <view-modal></view-modal>
    </div>
</template>

<script>
export default {
    data () {
        return {
            msg: 'luozh',
            str: ''
        }
    },
    methods: {
        viewEvent () {
            let that = this

            that.$broadcast('child-msg', that.msg)
        }
    },
    components: {
        ViewModal: require('./EventView.vue')
    },
    events: {
        'userStr': function (str) {
            console.log(str + ',again')
        }
    }
}
</script>

<style scoped>
.event-view {
    color: #005380;
    cursor: pointer;  
}
</style>