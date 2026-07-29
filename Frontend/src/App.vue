<script setup>
import { ref, computed } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import AppSidebar from './components/layout/AppSidebar.vue'
import TopBar from './components/layout/TopBar.vue'

const route = useRoute()

// Pages qui n'affichent PAS la sidebar (auth)
const noSidebarPages = ['login', 'register', '2fa']
const showSidebar = computed(() => !noSidebarPages.includes(route.name))

// État du menu mobile
const sidebarOpen = ref(false)

const toggleSidebar = () => {
  sidebarOpen.value = !sidebarOpen.value
}

const closeSidebar = () => {
  sidebarOpen.value = false
}
</script>

<template>
  <div class="app-layout">
    <template v-if="showSidebar">
      <!-- Backdrop overlay mobile -->
      <div
        v-if="sidebarOpen"
        class="sidebar-backdrop"
        @click="closeSidebar"
      ></div>
      <AppSidebar :isOpen="sidebarOpen" @close="closeSidebar" />
    </template>
    <div :class="['main-content', { 'has-sidebar': showSidebar }]">
      <TopBar
        v-if="showSidebar"
        :sidebarOpen="sidebarOpen"
        @toggle-sidebar="toggleSidebar"
      />
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
  min-height: 100vh;
}

/* Desktop: offset content by sidebar width */
.main-content.has-sidebar {
  margin-left: 220px;
}

.with-sidebar {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  height: calc(100vh - 60px);
}

.full-page {
  flex: 1;
  width: 100%;
}

/* Backdrop overlay for mobile sidebar */
.sidebar-backdrop {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  z-index: 999;
  backdrop-filter: blur(2px);
}

/* Mobile: < 768px */
@media (max-width: 767px) {
  .main-content.has-sidebar {
    margin-left: 0;
  }

  .with-sidebar {
    padding: 16px;
    height: calc(100vh - 56px);
  }

  .sidebar-backdrop {
    display: block;
  }
}

/* Tablet: 768px - 1024px */
@media (min-width: 768px) and (max-width: 1024px) {
  .with-sidebar {
    padding: 20px;
  }
}
</style>