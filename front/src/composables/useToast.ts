import { ref } from 'vue'
import type { ToastItem } from '@/types/toast'

const toastContainerRef = ref<{
  addToast: (toast: Omit<ToastItem, 'id'>) => string
  removeToast: (id: string) => void
} | null>(null)

export const useToast = () => {
  const showToast = (toast: Omit<ToastItem, 'id'>) => {
    if (!toastContainerRef.value) {
      console.warn('ToastContainer not found. Make sure it is mounted in App.vue')
      return
    }
    return toastContainerRef.value.addToast(toast)
  }

  const success = (title: string, description?: string, duration?: number) => {
    return showToast({ variant: 'success', title, description, duration })
  }

  const error = (title: string, description?: string, duration?: number) => {
    return showToast({ variant: 'error', title, description, duration })
  }

  const warning = (title: string, description?: string, duration?: number) => {
    return showToast({ variant: 'warning', title, description, duration })
  }

  const info = (title: string, description?: string, duration?: number) => {
    return showToast({ variant: 'default', title, description, duration })
  }

  const setToastContainer = (
    container: {
      addToast: (toast: Omit<ToastItem, 'id'>) => string
      removeToast: (id: string) => void
    } | null,
  ) => {
    toastContainerRef.value = container
  }

  return {
    showToast,
    success,
    error,
    warning,
    info,
    setToastContainer,
  }
}
