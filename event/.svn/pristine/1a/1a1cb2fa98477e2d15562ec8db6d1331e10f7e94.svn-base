<template>
    <div class="right-wrap">
        <div class="row">
            <div class="col-sm-12">
                <div class="right-header">
                    <div class="pull-left">
                        <h5>流程配置</h5>
                    </div>
                </div>
                <div class="right-body">
                    <button type="button" class="process-add-step btn btn-default" @click="addStep">
                        <span class="glyphicon glyphicon-plus"></span>
                        添加节点
                    </button>
                    <button type="button" class="btn btn-default" @click="addPrevStep">
                        <span class="glyphicon glyphicon-plus"></span>
                        向前添加
                    </button>
                    <button type="button" class="btn btn-default" @click="addNextStep">
                        <span class="glyphicon glyphicon-plus"></span>
                        向后添加
                    </button>
                    <button type="button" class="btn btn-default">
                        <span class="glyphicon glyphicon-ok"></span>
                        保存
                    </button>
                    <button type="button" class="btn btn-default" @click="deleteStep">
                        <span class="glyphicon glyphicon-trash"></span>
                        删除
                    </button>
                    <button type="button" class="btn btn-default" @click="clearStep">
                        <span class="glyphicon glyphicon-repeat"></span>
                        清空
                    </button>
                    <div class="process-body">
                        <div class="process-line"></div>
                        <div class="process-start step">开始</div>
                        <div class="process-step-box">
                            <div class="process-step" :class="step.isActive ? 'active' : ''" v-text="step.content" v-for="step in steps" track-by="$index" @click="selectFn($index)"></div>
                        </div>
                        <div class="process-end step">结束</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    data () {   
        return {
            steps: [{
                content: '',
                isActive: false,
            }],
            activeIndex: null
        }
    },
    methods: {

        // 添加节点
        addStep () {
            this.steps.push({
                content: '',
                isActive: false,
            })

            /*// TODO AJAX
            this.$http({
                url: '/someUrl', 
                method: 'POST',
                data: {
                    name: 'luozh'
                }
            })
            .then(function (response) {

            }, function (response) {

            });*/
        },

        // 选中节点
        selectFn (index) {
            if (this.steps[index].isActive === false) {
                this.steps.forEach(function(e) {
                    e.isActive = false
                })

                this.steps[index].isActive = true
                this.activeIndex = index
            } else {
                this.steps[index].isActive = false
                this.activeIndex = null
            }
        },

        // 向前添加
        addPrevStep () {
            if (this.activeIndex !== null) {
                this.steps.splice(this.activeIndex, 0, {
                    content: '',
                    isActive: false,
                })

                this.activeIndex = this.activeIndex + 1
            }
        },

        // 向后添加
        addNextStep () {
            if (this.activeIndex !== null) {
                this.steps.splice(this.activeIndex + 1, 0, {
                    content: '',
                    isActive: false,
                })
            }
        },

        // 删除节点
        deleteStep () {
            if (this.activeIndex !== null) {
                this.steps.splice(this.activeIndex, 1)

                this.activeIndex = null
            }
        },

        // 清空节点
        clearStep () {
            this.steps = []
            this.activeIndex = null
        }
    }
}
</script>

<style scoped>
.process-add-step {
    margin-left: 50px;
}

.process-body {
    position: relative;
    width: 600px;
    padding: 30px;
    margin: 15px 0 0 50px;
    min-height: 330px;
    border: 1px dashed #ddd;
}

.process-line {
    width: 2px;
    height: 80%;
    position: absolute;
    left: 50%;
    background: #eee;
}

.step {
    position: absolute;
    text-align: center;
    border-radius: 5px;
    left: 50%;
    color: #fff;
}

.process-start {
    width: 80px;
    height: 50px;
    background: #61A761;
    line-height: 50px;
    margin-left: -40px;
}

.process-end {
    width: 80px;
    height: 50px;
    background: #A56767;
    line-height: 50px;
    bottom: 30px;
    margin-left: -40px;
}

.process-step-box {
    padding: 80px 0 110px 0;
}

.process-step {
    position: relative;
    width: 60px;
    height: 40px;
    line-height: 40px;
    background: #DCDCDC;
    text-align: center;
    border-radius: 5px;
    margin-top: 30px;
    left: 50%;
    margin-left: -30px;
    color: #4C4C4C;
}

.process-step:hover,
.process-step.active {
    border: 1px solid #9E9E9E;
    cursor: pointer;
}
</style>