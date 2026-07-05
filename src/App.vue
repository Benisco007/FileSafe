<script setup>
import { computed } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import AppSidebar from './components/layout/AppSidebar.vue'

const route = useRoute()

// Pages qui n'affichent PAS la sidebar (auth)
const noSidebarPages = ['login', 'register', '2fa']
const showSidebar = computed(() => !noSidebarPages.includes(route.name))
</script>

<template>
  <div class="app-layout">
    <AppSidebar v-if="showSidebar" />
    <main :class="showSidebar ? 'with-sidebar' : 'full-page'">
      <RouterView />
    </main>
  </div>
</template>

<style>
.app-layout {
  display: flex;
  min-height: 100vh;
  background-color: #121212;
}
.with-sidebar {
  flex: 1;
  overflow-y: auto;
}
.full-page {
  width: 100%;
}
</style>