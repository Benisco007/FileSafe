<script setup>
import { computed } from 'vue'

const props = defineProps({
  statut: String,
  date_exp: String // Format ISO ou Date
})

const badgeInfo = computed(() => {
  if (props.statut) {
    // Si un statut explicite est fourni
    switch (props.statut.toLowerCase()) {
      case 'valide': return { text: 'Valide', color: 'success' }
      case 'expire bientôt': return { text: 'Expire bientôt', color: 'warning' }
      case 'expiré': return { text: 'Expiré', color: 'danger' }
      default: return { text: props.statut, color: 'default' }
    }
  }

  if (!props.date_exp) {
    return { text: 'Valide', color: 'success' }
  }

  const expDate = new Date(props.date_exp)
  const now = new Date()
  const diffTime = expDate - now
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

  if (diffDays < 0) {
    return { text: 'Expiré', color: 'danger' }
  } else if (diffDays <= 30) {
    return { text: 'Expire bientôt', color: 'warning' }
  } else {
    return { text: 'Valide', color: 'success' }
  }
})
</script>

<template>
  <span :class="['status-badge', badgeInfo.color]">
    {{ badgeInfo.text }}
  </span>
</template>

<style scoped>
.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
  white-space: nowrap;
}

.success {
  background-color: rgba(34, 197, 94, 0.15);
  color: var(--success);
}

.warning {
  background-color: rgba(244, 180, 0, 0.15);
  color: var(--primary);
}

.danger {
  background-color: rgba(239, 68, 68, 0.15);
  color: var(--danger);
}

.default {
  background-color: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
}
</style>
