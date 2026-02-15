<script setup lang="ts">
import { computed } from 'vue'
import { X } from 'lucide-vue-next'
import { cn } from '@/lib/utils/cn'

const props = withDefaults(
  defineProps<{
    variant?: 'default' | 'success' | 'error' | 'warning'
    title?: string
    description?: string
  }>(),
  {
    variant: 'default',
  },
)

const emit = defineEmits<{
  close: []
}>()

const variantStyles = computed(() => {
  const styles = {
    default: 'bg-white border-gray-200',
    success: 'bg-green-50 border-green-200',
    error: 'bg-red-50 border-red-200',
    warning: 'bg-yellow-50 border-yellow-200',
  }
  return styles[props.variant]
})

const iconColor = computed(() => {
  const colors = {
    default: 'text-gray-600',
    success: 'text-green-600',
    error: 'text-red-600',
    warning: 'text-yellow-600',
  }
  return colors[props.variant]
})
</script>

<template>
  <div
    :class="
      cn(
        'pointer-events-auto w-full max-w-sm rounded-sm border shadow-lg p-2 transition-all',
        variantStyles,
      )
    "
  >
    <div class="flex items-start gap-2">
      <div class="flex-1 space-y-1">
        <h3 v-if="title" class="text-sm font-semibold" :class="iconColor">
          {{ title }}
        </h3>
        <p v-if="description" class="text-sm text-gray-600">
          {{ description }}
        </p>
        <slot />
      </div>
      <button
        type="button"
        class="inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-lg text-gray-400 hover:text-gray-600 transition-colors"
        @click="emit('close')"
      >
        <X class="h-4 w-4" />
      </button>
    </div>
  </div>
</template>
