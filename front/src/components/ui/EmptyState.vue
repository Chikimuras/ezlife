<script setup lang="ts">
import { cn } from '@/lib/utils/cn'

interface Props {
  icon?: 'search' | 'inbox' | 'folder' | 'file'
  title?: string
  description?: string
  class?: string
}

const props = withDefaults(defineProps<Props>(), {
  icon: 'inbox',
})

const iconPaths = {
  search: 'M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z',
  inbox:
    'M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4',
  folder: 'M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z',
  file: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
}
</script>

<template>
  <div :class="cn('flex flex-col items-center justify-center py-12 px-4 text-center', props.class)">
    <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
      <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          :d="iconPaths[props.icon]"
        />
      </svg>
    </div>

    <h3 class="text-base font-medium text-gray-900 mb-2">
      <slot name="title">{{ title || $t('dashboard.groupBreakdown.empty') }}</slot>
    </h3>

    <p class="text-sm text-gray-600 max-w-sm">
      <slot name="description">{{ description || '' }}</slot>
    </p>

    <div v-if="$slots.action" class="mt-6">
      <slot name="action" />
    </div>
  </div>
</template>
