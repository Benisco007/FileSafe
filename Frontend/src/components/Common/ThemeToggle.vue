<template>
  <button class="theme-toggle" @click="$emit('toggle')" :title="isDark ? 'Mode clair' : 'Mode sombre'">
    <i :class="isDark ? 'ti ti-sun' : 'ti ti-moon'"></i>
  </button>
</template>

<script>
export default {
  name: 'ThemeToggle',
  
  props: {
    isDark: {
      type: Boolean,
      default: true
    }
  }
}
</script>

<style scoped>
.theme-toggle {
  position: absolute;
  top: 20px;
  right: 20px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 8px 10px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 18px;
}

.theme-toggle:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}
</style>