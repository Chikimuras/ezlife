<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import PublicLayout from '@/components/layouts/PublicLayout.vue'

const router = useRouter()
const authStore = useAuthStore()
const { t } = useI18n()

const email = ref('')
const name = ref('')
const isSubmitting = ref(false)
const localError = ref<string | null>(null)

const canSubmit = computed(
  () => email.value.trim().length > 0 && name.value.trim().length > 0 && !isSubmitting.value,
)

const handleSubmit = async () => {
  if (!canSubmit.value) return
  isSubmitting.value = true
  localError.value = null
  try {
    await authStore.registerWithPasskey({
      email: email.value.trim(),
      name: name.value.trim(),
    })
    await router.push('/dashboard')
  } catch {
    localError.value = t('register.error')
  } finally {
    isSubmitting.value = false
  }
}

const goToLogin = async () => {
  await router.push('/login')
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
                    d="M16 21v-2a4 4 0 00-4-4H6a4 4 0 00-4 4v2M9 11a4 4 0 100-8 4 4 0 000 8zm10-3v6m-3-3h6"
                  />
                </svg>
              </div>
              <h1 class="text-base font-bold text-gray-900 mb-2">
                {{ t('register.title') }}
              </h1>
              <p class="text-gray-600">
                {{ t('register.subtitle') }}
              </p>
            </div>

            <form class="space-y-4" @submit.prevent="handleSubmit">
              <div>
                <label for="register-email" class="block text-sm font-medium text-gray-700 mb-1">
                  {{ t('register.fields.email') }}
                </label>
                <input
                  id="register-email"
                  v-model="email"
                  type="email"
                  required
                  autocomplete="email"
                  class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                  :placeholder="t('register.fields.emailPlaceholder')"
                />
              </div>

              <div>
                <label for="register-name" class="block text-sm font-medium text-gray-700 mb-1">
                  {{ t('register.fields.name') }}
                </label>
                <input
                  id="register-name"
                  v-model="name"
                  type="text"
                  required
                  autocomplete="name"
                  class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                  :placeholder="t('register.fields.namePlaceholder')"
                />
              </div>

              <button
                type="submit"
                :disabled="!canSubmit"
                class="w-full px-4 py-2 text-sm font-medium text-white bg-primary-500 hover:bg-primary-600 disabled:opacity-60 disabled:cursor-not-allowed rounded-lg shadow-sm hover:shadow transition-colors"
              >
                {{ isSubmitting ? t('register.submitting') : t('register.submit') }}
              </button>

              <p
                v-if="localError"
                class="text-sm text-center text-red-600"
                data-testid="register-error"
              >
                {{ localError }}
              </p>
            </form>

            <div class="mt-6 relative">
              <div class="absolute inset-0 flex items-center">
                <div class="w-full border-t border-gray-200"></div>
              </div>
              <div class="relative flex justify-center text-sm">
                <span class="px-4 bg-white text-gray-500">{{ t('register.haveAccount') }}</span>
              </div>
            </div>

            <div class="text-center mt-4">
              <button
                class="text-primary-600 hover:text-primary-700 font-semibold transition-colors"
                @click="goToLogin"
              >
                {{ t('register.signIn') }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </public-layout>
</template>
