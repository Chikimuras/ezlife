<script setup lang="ts">
import { computed } from 'vue'
import { cn } from '@/lib/utils/cn'

interface Props {
  variant?: 'default' | 'outline' | 'ghost' | 'destructive'
  size?: 'default' | 'sm' | 'lg'
  disabled?: boolean
  class?: string
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  size: 'default',
  disabled: false,
})

const buttonClass = computed(() =>
  cn(
    'inline-flex items-center justify-center font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-1 disabled:pointer-events-none disabled:opacity-50',
    {
      // Primary Button (Call-to-action)
      'text-white bg-primary-500 hover:bg-primary-600 shadow-sm hover:shadow':
        props.variant === 'default',
      // Outline Button
      'text-gray-700 border border-gray-200 hover:border-gray-300 hover:bg-gray-50':
        props.variant === 'outline',
      // Ghost Button (Minimal)
      'text-gray-600 hover:text-gray-900 hover:bg-gray-100': props.variant === 'ghost',
      // Destructive Button
      'text-white bg-red-500 hover:bg-red-600 shadow-sm hover:shadow':
        props.variant === 'destructive',
    },
    {
      'px-4 py-2 text-sm rounded-lg': props.size === 'default',
      'px-3 py-1.5 text-sm rounded-md': props.size === 'sm',
      'px-5 py-2.5 text-base rounded-lg': props.size === 'lg',
    },
    props.class,
  ),
)
</script>

<template>
  <button :class="buttonClass" :disabled="disabled">
    <slot />
  </button>
</template>
