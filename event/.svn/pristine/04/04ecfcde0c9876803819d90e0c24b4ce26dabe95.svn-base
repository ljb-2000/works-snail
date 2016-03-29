<!-- 头部组件 -->
<template>
    <nav class="clear-navbar navbar navbar-default">
        <div class="container-fluid pr0">
            <div class="navbar-header">
                <a class="navbar-brand" v-link="{ path: '/process/luozh' }">Snail</a>
            </div>
            <div class="collapse navbar-collapse">
                <ul class="nav navbar-nav">
                    <li class="logo-title" v-link="{ path: '/process/' + username }">
                        <a>蜗牛事件平台 </a>
                    </li>
                </ul>
                <ul class="nav navbar-nav navbar-right">
                    <li class="nav-border">
                        <a data-toggle="modal" data-target="#event_input">事件录入</a>
                    </li>
                    <li class="dropdown">
                        <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">
                            luozh 
                            <span class="caret"></span>
                        </a>
                        <ul class="dropdown-menu">
                            <li><a @click="exitFn">退出</a></li>
                        </ul>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="modal fade" id="event_input" tabindex="-1" role="dialog">
        <input-modal></input-modal>
    </div>
</template>

<script>
export default {
    data () {
        return {
            username: 'luozh'
        }
    },
    methods: {
        exitFn () {
            console.log(this.$route.params);

            let _this = this

            this.$dispatch('userStr', _this.username)
        }
    },
    components: {
        InputModal: require('./EventInput.vue')
    }
}
</script>

<style scoped>
.nav li:hover{
    cursor: pointer;
}

.clear-navbar {
    position: fixed;
    width: 100%;
    border: none;
    border-radius: 0;
    background: #09C;
    font-size: 14px;
    z-index: 101;
}

.clear-navbar .nav > li > a,
.clear-navbar .navbar-brand {
    color: #fff;
}

.clear-navbar .logo-title a,
.clear-navbar .nav > li > a:hover,
.navbar-default .navbar-nav>.open>a {
    background: #008fbf;
    color: #fff;
}

.nav-border {
    border-right: 1px solid #008fbf;
}
</style>