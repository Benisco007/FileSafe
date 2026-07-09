<script setup>
import { computed } from 'vue'

const props = defineProps({
  type: {
    type: String,
    required: true,
    // Valide, Expire_Bientot, Expire, Critique, IA
  },
  text: {
    type: String,
    default: ''
  },
  small: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: ''
  }
})

const badgeConfig = {
  'Valide':         { text: 'Valide',         classes: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
  'Expire_Bientot': { text: 'Expire Bientôt', classes: 'bg-amber-50 text-amber-700 border-amber-200' },
  'Expire':         { text: 'Expiré',         classes: 'bg-rose-50 text-rose-700 border-rose-200' },
  'Critique':       { text: 'Critique',       classes: 'bg-orange-50 text-orange-700 border-orange-200' },
  'IA':             { text: 'Indexé IA',      classes: 'bg-sky-50 text-sky-700 border-sky-200' },
  'default':        { text: 'Inconnu',        classes: 'bg-slate-100 text-slate-600 border-slate-200' }
}

const config = computed(() => badgeConfig[props.type] || badgeConfig.default)

const badgeClasses = computed(() => {
  const base = props.small 
    ? 'text-[10px] px-1.5 py-0.5 rounded-md border font-medium' 
    : 'px-2 py-1 rounded-full text-xs font-medium';
  
  const border = props.small ? '' : 'border-transparent';

  return [base, config.value.classes, border]
})

const displayText = computed(() => {
  if (props.text) return props.text;
  return config.value.text || props.type.replace('_', ' ');
})
</script>

<template>
  <span :class="badgeClasses" :title="title || displayText">
    {{ displayText }}
  </span>
</template>