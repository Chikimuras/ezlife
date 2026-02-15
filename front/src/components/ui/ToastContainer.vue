<script setup lang="ts">
import { ref, onUnmounted } from 'vue'
import Toast from '@/components/ui/Toast.vue'
import { cn } from '@/lib/utils/cn'
import type { ToastItem } from '@/types/toast'

const props = withDefaults(
  defineProps<{
    position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left'
  }>(),
  {
    position: 'top-right',
  },
)

const toasts = ref<ToastItem[]>([])
const timeouts = new Map<string, ReturnType<typeof setTimeout>>()

const positionClasses = {
  'top-right': 'top-2 right-4',
  'top-left': 'top-2 left-4',
  'bottom-right': 'bottom-4 right-4',
  'bottom-left': 'bottom-4 left-4',
}

const addToast = (toast: Omit<ToastItem, 'id'>) => {
  const id = Math.random().toString(36).substring(2, 9)
  const duration = toast.duration ?? 3000

  toasts.value.push({ ...toast, id })

  if (duration > 0) {
    const timeout = setTimeout(() => {
      removeToast(id)
    }, duration)
    timeouts.set(id, timeout)
  }

  return id
}

const removeToast = (id: string) => {
  toasts.value = toasts.value.filter((t) => t.id !== id)
  const timeout = timeouts.get(id)
  if (timeout) {
    clearTimeout(timeout)
    timeouts.delete(id)
  }
}

onUnmounted(() => {
  timeouts.forEach((timeout) => clearTimeout(timeout))
  timeouts.clear()
})

defineExpose({
  addToast,
  removeToast,
})
</script>

<template>
  <div :class="cn('fixed z-50 pointer-events-none space-y-2', positionClasses[position])">
    <TransitionGroup
      enter-active-class="transition-all duration-200 ease-out"
      enter-from-class="opacity-0 translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition-all duration-150 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 translate-x-4"
    >
      <Toast
        v-for="toast in toasts"
        :key="toast.id"
        :variant="toast.variant"
        :title="toast.title"
        :description="toast.description"
        @close="removeToast(toast.id)"
      />
    </TransitionGroup>
  </div>
</template>
