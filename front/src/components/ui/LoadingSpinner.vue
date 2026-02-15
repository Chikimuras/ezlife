<script setup lang="ts">
import { cn } from '@/lib/utils/cn'

interface Props {
  size?: 'sm' | 'md' | 'lg'
  variant?: 'primary' | 'secondary' | 'white'
  class?: string
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  variant: 'primary',
})

const sizeClasses = {
  sm: 'w-4 h-4 border-2',
  md: 'w-8 h-8 border-2',
  lg: 'w-12 h-12 border-3',
}

const colorClasses = {
  primary: 'border-primary-600 border-t-transparent',
  secondary: 'border-secondary-600 border-t-transparent',
  white: 'border-white border-t-transparent',
}
</script>

<template>
  <div
    :class="
      cn(
        'animate-spin rounded-full',
        sizeClasses[props.size],
        colorClasses[props.variant],
        props.class,
      )
    "
    role="status"
    aria-label="Loading"
  >
    <span class="sr-only">{{ $t('common.loading') }}</span>
  </div>
</template>
