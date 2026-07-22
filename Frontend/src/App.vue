<script setup>
import { computed } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import AppSidebar from './components/layout/AppSidebar.vue'
import TopBar from './components/layout/TopBar.vue'

const route = useRoute()

// Pages qui n'affichent PAS la sidebar (auth)
const noSidebarPages = ['login', 'register', '2fa']
const showSidebar = computed(() => !noSidebarPages.includes(route.name))
</script>

<template>
  <div class="app-layout">
    <AppSidebar v-if="showSidebar" />
    <div class="main-content">
      <TopBar v-if="showSidebar" />
      <main :class="showSidebar ? 'with-sidebar' : 'full-page'">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<style>
.app-layout {
  display: flex;
  min-height: 100vh;
  background-color: var(--bg-primary);
}
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.with-sidebar {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}
.full-page {
  flex: 1;
  width: 100%;
}
</style>