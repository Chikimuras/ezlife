<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import PublicLayout from '@/components/layouts/PublicLayout.vue'

const router = useRouter()
const authStore = useAuthStore()
const { t } = useI18n()


const isSubmitting = ref(false)
const localError = ref<string | null>(null)

const handleLogin = async () => {
  isSubmitting.value = true
  localError.value = null
  try {
    await authStore.loginWithPasskey()
    await router.push('/dashboard')
  } catch {
    localError.value = t('login.error')
  } finally {
    isSubmitting.value = false
  }
}

const goToRegister = async () => {
  await router.push('/register')
}
</script>

<template>
  <public-layout>
    <div
      class="flex min-h-[calc(100vh-4rem)] items-center justify-center px-4 py-12 sm:px-4 lg:px-4"
    >
      <div class="w-full max-w-md">
        <div class="relative">
          <div class="absolute inset-0 -z-10 blur-3xl opacity-30">
            <div class="absolute top-0 left-1/4 w-72 h-72 bg-primary-300 rounded-full"></div>
            <div class="absolute bottom-0 right-1/4 w-72 h-72 bg-secondary-300 rounded-full"></div>
          </div>

          <div class="bg-white rounded-3xl shadow-xl border border-gray-100 p-4 sm:p-12">
            <div class="text-center mb-4">
              <div
                class="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-primary-400 to-primary-600 rounded-lg mb-4 shadow-lg"
              >
                <svg
                  class="w-10 h-10 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                  />
                </svg>
              </div>
              <h1 class="text-base font-bold text-gray-900 mb-2">
                {{ t('login.title') }}
              </h1>
              <p class="text-gray-600">
                {{ t('login.subtitle') }}
              </p>
            </div>

            <div class="space-y-6">
              <button
                :disabled="isSubmitting"
                class="w-full px-4 py-2 text-sm font-medium text-white bg-primary-500 hover:bg-primary-600 disabled:opacity-60 disabled:cursor-not-allowed rounded-lg shadow-sm hover:shadow transition-colors"
                @click="handleLogin"
              >
                {{ isSubmitting ? t('login.signingIn') : t('login.passkeyButton') }}
              </button>

              <p
                v-if="localError"
                class="text-sm text-center text-red-600"
                data-testid="login-error"
              >
                {{ localError }}
              </p>

              <div class="relative">
                <div class="absolute inset-0 flex items-center">
                  <div class="w-full border-t border-gray-200"></div>
                </div>
                <div class="relative flex justify-center text-sm">
                  <span class="px-4 bg-white text-gray-500">{{ t('login.noAccount') }}</span>
                </div>
              </div>

              <div class="text-center">
                <button
                  class="text-primary-600 hover:text-primary-700 font-semibold transition-colors"
                  @click="goToRegister"
                >
                  {{ t('login.signUp') }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </public-layout>
</template>
