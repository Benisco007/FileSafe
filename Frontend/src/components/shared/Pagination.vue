<script setup>
import { computed } from 'vue'

const props = defineProps({
  total: { type: Number, required: true },
  perPage: { type: Number, default: 10 },
  currentPage: { type: Number, default: 1 }
})

const emit = defineEmits(['update:currentPage'])

const totalPages = computed(() => Math.ceil(props.total / props.perPage))

const showPagination = computed(() => totalPages.value > 1)

// Generate visible page numbers with ellipsis
const visiblePages = computed(() => {
  const pages = []
  const total = totalPages.value
  const current = props.currentPage

  if (total <= 7) {
    for (let i = 1; i <= total; i++) pages.push(i)
  } else {
    pages.push(1)
    if (current > 3) pages.push('...')
    const start = Math.max(2, current - 1)
    const end = Math.min(total - 1, current + 1)
    for (let i = start; i <= end; i++) pages.push(i)
    if (current < total - 2) pages.push('...')
    pages.push(total)
  }

  return pages
})

const goToPage = (page) => {
  if (typeof page !== 'number') return
  if (page < 1 || page > totalPages.value) return
  emit('update:currentPage', page)
}

const prevPage = () => {
  if (props.currentPage > 1) goToPage(props.currentPage - 1)
}

const nextPage = () => {
  if (props.currentPage < totalPages.value) goToPage(props.currentPage + 1)
}
</script>

<template>
  <nav v-if="showPagination" class="pagination" aria-label="Pagination">
    <button
      class="pagination-btn nav-btn"
      :disabled="currentPage <= 1"
      @click="prevPage"
      aria-label="Page précédente"
    >
      <i class="ti ti-chevron-left"></i>
      <span class="nav-label">Précédent</span>
    </button>

    <div class="pagination-pages">
      <button
        v-for="(page, idx) in visiblePages"
        :key="idx"
        :class="['pagination-btn page-btn', { active: page === currentPage, ellipsis: page === '...' }]"
        :disabled="page === '...'"
        @click="goToPage(page)"
      >
        {{ page }}
      </button>
    </div>

    <button
      class="pagination-btn nav-btn"
      :disabled="currentPage >= totalPages"
      @click="nextPage"
      aria-label="Page suivante"
    >
      <span class="nav-label">Suivant</span>
      <i class="ti ti-chevron-right"></i>
    </button>
  </nav>
</template>

<style scoped>
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 16px 0 4px;
  flex-shrink: 0;
}

.pagination-pages {
  display: flex;
  align-items: center;
  gap: 4px;
}

.pagination-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  background: none;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}

.nav-btn {
  padding: 8px 16px;
  min-height: 40px;
}

.page-btn {
  width: 40px;
  height: 40px;
  padding: 0;
}

.pagination-btn:hover:not(:disabled):not(.ellipsis) {
  background-color: var(--bg-card);
  color: var(--text-primary);
  border-color: var(--text-muted);
}

.pagination-btn.active {
  background-color: rgba(244, 180, 0, 0.15);
  border-color: var(--primary);
  color: var(--primary);
  font-weight: 600;
}

.pagination-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.pagination-btn.ellipsis {
  border: none;
  cursor: default;
  opacity: 0.5;
}

.pagination-btn i {
  font-size: 16px;
}

/* Mobile */
@media (max-width: 768px) {
  .pagination {
    gap: 4px;
  }

  .nav-label {
    display: none;
  }

  .nav-btn {
    padding: 8px 12px;
    min-height: 44px;
  }

  .page-btn {
    width: 44px;
    height: 44px;
    font-size: 14px;
  }
}
</style>
