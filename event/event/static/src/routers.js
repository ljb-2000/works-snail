/**
 * 
 * @authors luozh@snail.com
 * @date    2016-03-21 17:04:26
 * @description 路由配置
 */

'use strict'

export default function(router) {
    router.map({
        '/': {
            component: function (resolve) {
                require(['./components/event_manage/History.vue'], resolve)
            }
        },
        '*': {
            component: require('./views/404.vue')
        },
        '/process/:username': {
            component: function (resolve) {
                require(['./components/Process.vue'], resolve)
            }
        },
        '/history': {
            component: function (resolve) {
                require(['./components/event_manage/History.vue'], resolve)
            }
        },
        '/staffTree': {
            component: function (resolve) {
                require(['./components/StaffTree.vue'], resolve)
            }
        }
    })
}
