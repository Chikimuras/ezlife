<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import LanguageSelector from '@/components/ui/LanguageSelector.vue'

const { t } = useI18n()
const router = useRouter()
</script>

<template>
  <div class="min-h-screen bg-white">
    <nav
      class="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-100"
    >
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center space-x-2 cursor-pointer" @click="router.push('/')">
            <svg
              class="h-8 w-8 text-primary-500"
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
            <span class="text-xl font-bold text-gray-900">TimeTracker</span>
          </div>

          <div class="flex items-center space-x-4">
            <LanguageSelector />
            <button
              @click="router.push('/login')"
              class="px-3 py-1.5 text-xs font-medium text-gray-700 hover:text-primary-600 transition-colors"
            >
              {{ t('nav.login') }}
            </button>
            <button
              class="px-6 py-2 text-xs font-medium text-white bg-primary-500 hover:bg-primary-600 rounded-lg transition-colors shadow-sm hover:shadow-md"
            >
              {{ t('nav.register') }}
            </button>
          </div>
        </div>
      </div>
    </nav>

    <main class="pt-16">
      <slot />
    </main>
  </div>
</template>
