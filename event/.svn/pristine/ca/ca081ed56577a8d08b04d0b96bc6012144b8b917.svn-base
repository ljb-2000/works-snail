<!-- 导航组件 -->
<template>
    <div class="sidebar">
        <div class="item" v-for="list in menuList">
            <div class="item-header" @click="sildeFn($index)" :class="list.show ? '' : 'close-status'">
                <span class="arrow glyphicon glyphicon-triangle-bottom" :class="list.show ? '' : 'up'"></span>
                <span class="header-title" v-text="list.header"></span>
                <span class="header-icon glyphicon glyphicon-cog"></span>
            </div>
            <ul class="item-children" v-show="list.show" transition="slide">
                <li v-for="item in list.items">
                    <a class="item-list" v-link="{ path: item.link }">
                        <div class="item-list-icon" :class="item.icon"></div>
                        <span class="item-list-name" v-text="item.name"></span>
                    </a>
                </li>
            </ul>
        </div>
    </div>
</template>

<script>
export default {
    data () {
        return {
            menuList: [{
                header: '事件管理',
                show: true,
                items: [{
                    icon: 'glyphicon glyphicon-credit-card',
                    link: '',
                    name: '我的事件'
                }, {
                    icon: 'glyphicon glyphicon-record',
                    link: '',
                    name: '当前事件'
                }, {
                    icon: 'glyphicon glyphicon-heart-empty',
                    link: '',
                    name: '我关注的事件'
                }, {
                    icon: 'glyphicon glyphicon-dashboard',
                    link: '/history',
                    name: '历史事件'
                }]
            }, {
                header: '事件报表',
                show: true,
                items: [{
                    icon: 'glyphicon glyphicon-stats',
                    link: '',
                    name: '事件统计'
                }, {
                    icon: 'glyphicon glyphicon-equalizer',
                    link: '',
                    name: '员工KPA'
                }]
            }]
        }
    },
    methods: {
        sildeFn (index) {
            this.menuList[index].show === true ? this.menuList[index].show = false : this.menuList[index].show = true
        }
    }
}
</script>

<style scoped>
.sidebar {
    width: 185px;
    display: block;
    position: fixed;
    top: 50px;
    bottom: 0px;
    background-color: #293038;
    z-index: 102;
    overflow-x: hidden;
}

.sidebar .item {
    width: 185px;
}

.item-header {
    height: 40px;
    background: #22282e;
    color: #fff;
    line-height: 40px;
    position: relative;
    cursor: pointer;
    -webkit-user-select: none;
    -moz-user-select: none;
}

.item-header.close-status {
    background: #37424f;
}

.item-header:hover {
    background: #414d5c;
}

.arrow {
    display: inline-block;
    margin: 0 8px 0 20px;
    vertical-align: middle;
    transform: scale(0.6);
    -ms-transform: scale(0.6);
    -moz-transform: scale(0.6);
    -webkit-transform: scale(0.6);
    transition: transform 0.12s;
    -ms-transition: -ms-transform 0.12s;
    -moz-transition: -moz-transform 0.12s;
    -webkit-transition: -webkit-transform 0.12s;
}

.arrow.up {
    transform: rotate(-90deg) scale(0.6);
    -ms-transform: rotate(-90deg) scale(0.6);
    -moz-transform: rotate(-90deg) scale(0.6);
    -webkit-transform: rotate(-90deg) scale(0.6);
}

.header-title {
    display: inline-block;
    font-size: 12px;
}

.header-icon {
    display: inline-block;
    width: 40px;
    height: 40px;
    line-height: 40px;
    text-align: center;
    position: absolute;
    right: 0;
    color: #a0abb3;
}

.item-children {
    margin-bottom: 0;
    padding-left: 0;
}

.item-list {
    position: relative;
    display: block;
    width: 100%;
    height: 40px;
    line-height: 40px;
    overflow: hidden;
    cursor: pointer;
}

.item-list:hover {
    background: #37424f;
}

.item-list.active {
    background: #0099cc;
}

.item-list-icon {
    position: absolute;
    width: 50px;
    height: 40px;
    line-height: 40px;
    text-align: center;
    left: 0;
    font-size: 16px;
    color: #aeb9c2;
}

.item-list.active .item-list-icon {
    color: #fff;
}

.item-list-name {
    position: absolute;
    width: 135px;
    height: 40px;
    line-height: 40px;
    right: 0;
    color: #fff;
    font-size: 12px;
    white-space: nowrap;
    text-overflow: ellipsis;
}

.slide-enter {
    height: 100%;
    overflow: hidden;
}

.slide-leave {
    height: 0;
    overflow: hidden;
}

</style>