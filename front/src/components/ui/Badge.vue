<script setup lang="ts">
import { computed } from 'vue'
import { cn } from '@/lib/utils/cn'

interface Props {
  variant?: 'default' | 'secondary' | 'outline'
  class?: string
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
})

const badgeClass = computed(() =>
  cn(
    'inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold transition-colors',
    {
      'bg-primary-100 text-primary-700': props.variant === 'default',
      'bg-secondary-100 text-secondary-700': props.variant === 'secondary',
      'border border-gray-200 text-gray-700': props.variant === 'outline',
    },
    props.class,
  ),
)
</script>

<template>
  <div :class="badgeClass">
    <slot />
  </div>
</template>
