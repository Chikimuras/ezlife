<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import Button from '@/components/ui/Button.vue'

interface Props {
  error?: Error
  resetError?: () => void
}

const props = defineProps<Props>()
const router = useRouter()

const showDetails = ref(false)

const handleReload = () => {
  if (props.resetError) {
    props.resetError()
  } else {
    window.location.reload()
  }
}

const handleGoHome = () => {
  router.push({ name: 'home' })
}
</script>

<template>
  <div
    class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-secondary-50 px-4"
  >
    <div class="max-w-md w-full bg-white rounded-xl shadow-lg p-8 text-center">
      <div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg class="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          />
        </svg>
      </div>

      <h1 class="text-2xl font-semibold text-gray-900 mb-2">
        {{ $t('errors.boundary.title') }}
      </h1>
      <p class="text-sm text-gray-600 mb-6">
        {{ $t('errors.boundary.message') }}
      </p>

      <div v-if="error && showDetails" class="mb-6 text-left">
        <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <p class="text-xs font-medium text-gray-700 mb-2">{{ $t('errors.boundary.details') }}</p>
          <p class="text-xs text-gray-600 font-mono break-all">
            {{ error.message }}
          </p>
          <p v-if="error.stack" class="text-xs text-gray-500 font-mono mt-2 overflow-auto max-h-32">
            {{ error.stack }}
          </p>
        </div>
      </div>

      <div class="flex flex-col sm:flex-row gap-3 justify-center">
        <Button variant="default" @click="handleReload">
          {{ $t('errors.actions.reload') }}
        </Button>
        <Button variant="outline" @click="handleGoHome">
          {{ $t('errors.actions.goHome') }}
        </Button>
      </div>

      <button
        v-if="error"
        class="mt-4 text-xs text-gray-500 hover:text-gray-700 transition-colors"
        @click="showDetails = !showDetails"
      >
        {{ showDetails ? $t('errors.boundary.hideDetails') : $t('errors.boundary.showDetails') }}
      </button>
    </div>
  </div>
</template>
