<script setup>
</script>

<template>
  <main class="app-container">
    <router-view />
  </main>
</template>

<style scoped>
/* 添加水平偏移的樣式 */
.app-container {
  display: flex;
  height: 100vh;
  width: 100vw;
  background-color: #2b2b2b !important; /* 預設背景顏色 */
  background-size: auto;
  color: #fff;
  overflow: hidden;
  margin: 0;
  padding: 0;
  justify-content: flex-start;
  transform: translateX(-230px);
}
header {
  line-height: 1.5;
}

</style>
