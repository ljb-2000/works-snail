<template>
    <div id="tree"></div>
</template>

<script>
require('../assets/js/bootstrap-treeview/bootstrap-treeview.min.js')

export default {
    ready () {
        function getTree() {

            // Some logic to retrieve, or generate tree structure
            return [{
                text: "运维开发部",
                selectable: false,
                nodes: [{
                    text: "wx"
                }, {
                    text: "luozh"
                }],
                state: {
                    expanded: false
                }
            }, {
                text: "项目一部",
                selectable: false,
            }, {
                text: "项目二部",
                selectable: false,
            }, {
                text: "移动运维",
                selectable: false,
            }, {
                text: "监控部",
                selectable: false,
            }]
        }
         
        $('#tree').treeview({
            data: getTree(),
            selectedBackColor: '#0099CC'
        })
    }
}
</script>

<style>
@import url('../assets/js/bootstrap-treeview/bootstrap-treeview.min.css');

#tree {
    width: 70%;
    margin: 70px auto;
}
</style>