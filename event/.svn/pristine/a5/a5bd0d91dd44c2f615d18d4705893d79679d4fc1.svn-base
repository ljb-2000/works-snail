<!-- 总组件 -->
<template lang='jade'>
div
    head-top

    div.main
        Left
        Right
</template>

<script>
var bt = require('bootstrap')

export default {
    data () {
        return {
            username: ''
        }
    },
    components: {
        HeadTop: require('./views/Header.vue'),
        Left: require('./views/Left.vue'),
        Right: require('./views/Right.vue')
    },
    events: {
        'userStr': function (str) {
            this.username = str

            console.log(this.username);

            let _this = this

            this.$broadcast('userStr', _this.username)
        }
    }
}
</script>

<style lang="stylus">
@import '../src/assets/css/bootstrap.min.css'
@import '../src/assets/css/common.css'

.main 
    position: absolute
    width: 100%
    top: 50px
    bottom: 0px
    background-color: #000
    z-index: 100
</style>