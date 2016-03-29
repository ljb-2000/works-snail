<!-- 右侧显示区组件 -->
<template>
    <div class="right-view">
        <router-view transition="fade" transition-mode="out-in"></router-view>
    </div>
</template>

<script>
    
</script>

<style scoped>
.right-view {
    width: auto;
    position: absolute;
    top: 0px;
    left: 185px;
    bottom: 0px;
    right: 0px;
    overflow: hidden;
    overflow-y: auto;
    background: #fff;
}

.fade-transition {
  transition: opacity 0.1s ease;
}

.fade-enter, .fade-leave {
  opacity: 0;
}
</style>