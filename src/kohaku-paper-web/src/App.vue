<script setup>
import TheHeader from '@/components/layout/TheHeader.vue'
</script>

<template>
  <div class="app">
    <TheHeader />
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.app {
  min-height: 100vh;
  background: var(--el-bg-color-page);
}

.main-content {
  min-height: calc(100vh - 60px);
}
</style>
