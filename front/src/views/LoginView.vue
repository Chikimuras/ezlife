<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { GoogleLogin } from 'vue3-google-login'
import type { CallbackTypes } from 'vue3-google-login'
import { useAuthStore } from '@/stores/auth'
import PublicLayout from '@/components/layouts/PublicLayout.vue'

const router = useRouter()
const authStore = useAuthStore()
const { t } = useI18n()

const callback: CallbackTypes.CredentialCallback = async (response) => {
  if (response.credential) {
    try {
      await authStore.loginWithGoogle(response.credential)
      await router.push('/activities')
    } catch (error) {
      console.error('Login failed', error)
    }
  }
}
</script>

<template>
  <PublicLayout>
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
                    d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
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
              <div class="flex justify-center">
                <GoogleLogin :callback="callback" />
              </div>

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
                >
                  {{ t('login.signUp') }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </PublicLayout>
</template>
