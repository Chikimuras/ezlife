<script setup lang="ts">
import { cn } from '@/lib/utils/cn'

interface Props {
  message?: string
  variant?: 'error' | 'warning' | 'info'
  class?: string
}

const props = withDefaults(defineProps<Props>(), {
  message: '',
  variant: 'error',
})

const iconPath = {
  error:
    'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z',
  warning:
    'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z',
  info: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
}
</script>

<template>
  <div
    :class="
      cn(
        'rounded-lg p-4 flex items-start gap-3',
        {
          'bg-red-50 border border-red-200': variant === 'error',
          'bg-yellow-50 border border-yellow-200': variant === 'warning',
          'bg-blue-50 border border-blue-200': variant === 'info',
        },
        props.class,
      )
    "
  >
    <svg
      :class="
        cn('w-5 h-5 flex-shrink-0 mt-0.5', {
          'text-red-600': variant === 'error',
          'text-yellow-600': variant === 'warning',
          'text-blue-600': variant === 'info',
        })
      "
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path
        stroke-linecap="round"
        stroke-linejoin="round"
        stroke-width="2"
        :d="iconPath[variant]"
      />
    </svg>

    <div class="flex-1">
      <p
        :class="
          cn('text-sm font-medium', {
            'text-red-800': variant === 'error',
            'text-yellow-800': variant === 'warning',
            'text-blue-800': variant === 'info',
          })
        "
      >
        <slot name="title">
          <span v-if="variant === 'error'">{{ $t('common.error') }}</span>
          <span v-else-if="variant === 'warning'">Warning</span>
          <span v-else>Information</span>
        </slot>
      </p>
      <p
        v-if="message || $slots.default"
        :class="
          cn('text-sm mt-1', {
            'text-red-700': variant === 'error',
            'text-yellow-700': variant === 'warning',
            'text-blue-700': variant === 'info',
          })
        "
      >
        <slot>{{ message }}</slot>
      </p>
    </div>

    <slot name="action" />
  </div>
</template>
