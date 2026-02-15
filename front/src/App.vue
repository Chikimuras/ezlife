<script setup lang="ts">
import { onMounted, ref, onErrorCaptured } from 'vue'
import { useRouter } from 'vue-router'
import ToastContainer from '@/components/ui/ToastContainer.vue'
import OfflineBanner from '@/components/ui/OfflineBanner.vue'
import { useToast } from '@/composables/useToast'
import { useAuthStore } from '@/stores/auth'
import { useErrorHandler } from '@/composables/useErrorHandler'
import { useTokenRefresh } from '@/composables/useTokenRefresh'

const router = useRouter()
const toastContainerRef = ref<InstanceType<typeof ToastContainer> | null>(null)
const { setToastContainer } = useToast()
const authStore = useAuthStore()
const { handleError } = useErrorHandler()
const { startTokenRefreshCycle } = useTokenRefresh()

onErrorCaptured((error) => {
  handleError(error, { context: 'Vue Component Error' })
  return false
})

onMounted(async () => {
  setToastContainer(toastContainerRef.value)

  window.addEventListener('unhandledrejection', (event) => {
    event.preventDefault()
    handleError(event.reason, { context: 'Unhandled Promise Rejection' })
  })

  window.addEventListener('error', (event) => {
    event.preventDefault()
    handleError(event.error, { context: 'Global Error' })
  })

  if (authStore.token) {
    const isValid = await authStore.fetchCurrentUser()
    if (!isValid) {
      const currentRoute = router.currentRoute.value
      if (currentRoute.meta.requiresAuth) {
        router.push({ name: 'login' })
      }
    } else {
      startTokenRefreshCycle()
    }
  }
})
</script>

<template>
  <div class="min-h-screen bg-white text-zinc-950 font-sans">
    <OfflineBanner />
    <router-view />
    <ToastContainer ref="toastContainerRef" />
  </div>
</template>
