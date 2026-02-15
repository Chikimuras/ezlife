<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import PublicLayout from '@/components/layouts/PublicLayout.vue'

const { t } = useI18n()
const router = useRouter()
</script>

<template>
  <PublicLayout>
    <div class="relative overflow-hidden">
      <div class="absolute inset-0 -z-10">
        <svg class="absolute top-0 right-0 w-1/2 h-1/2 opacity-20" viewBox="0 0 400 400">
          <circle cx="200" cy="100" r="120" fill="url(#gradient1)" />
          <circle cx="300" cy="200" r="80" fill="url(#gradient2)" />
          <defs>
            <linearGradient id="gradient1" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" style="stop-color: #e9d5ff; stop-opacity: 1" />
              <stop offset="100%" style="stop-color: #c084fc; stop-opacity: 0.6" />
            </linearGradient>
            <linearGradient id="gradient2" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" style="stop-color: #d1ddd1; stop-opacity: 1" />
              <stop offset="100%" style="stop-color: #88ac88; stop-opacity: 0.6" />
            </linearGradient>
          </defs>
        </svg>
      </div>

      <section class="max-w-7xl mx-auto px-4 sm:px-4 lg:px-4 py-20 sm:py-32">
        <div class="text-center">
          <h1
            class="text-5xl sm:text-6xl lg:text-7xl font-bold text-gray-900 mb-4 bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent"
          >
            {{ t('landing.hero.title') }}
          </h1>
          <p class="text-base sm:text-sm text-gray-600 mb-10 max-w-3xl mx-auto leading-relaxed">
            {{ t('landing.hero.subtitle') }}
          </p>
          <div class="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <button
              @click="router.push('/login')"
              class="px-4 py-4 text-sm font-semibold text-white bg-primary-500 hover:bg-primary-600 rounded-lg shadow-lg hover:shadow-xl transition-all transform hover:scale-105"
            >
              {{ t('landing.hero.cta') }}
            </button>
            <button
              class="px-4 py-4 text-sm font-semibold text-primary-600 bg-primary-50 hover:bg-primary-100 rounded-lg transition-colors"
            >
              {{ t('landing.hero.learnMore') }}
            </button>
          </div>
        </div>

        <div class="mt-20 relative">
          <div class="absolute inset-0 flex items-center justify-center -z-10">
            <svg class="w-full h-full max-w-4xl opacity-10" viewBox="0 0 600 400">
              <path
                d="M100 200 Q 200 100, 300 200 T 500 200"
                stroke="url(#gradient3)"
                stroke-width="3"
                fill="none"
              />
              <circle cx="100" cy="200" r="8" fill="#a855f7" />
              <circle cx="300" cy="200" r="8" fill="#6b9670" />
              <circle cx="500" cy="200" r="8" fill="#a855f7" />
              <defs>
                <linearGradient id="gradient3" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" style="stop-color: #a855f7; stop-opacity: 1" />
                  <stop offset="50%" style="stop-color: #6b9670; stop-opacity: 1" />
                  <stop offset="100%" style="stop-color: #a855f7; stop-opacity: 1" />
                </linearGradient>
              </defs>
            </svg>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div
              class="bg-white border border-gray-100 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow"
            >
              <div
                class="w-14 h-14 bg-primary-100 rounded-lg flex items-center justify-center mb-4"
              >
                <svg
                  class="w-8 h-8 text-primary-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M13 10V3L4 14h7v7l9-11h-7z"
                  />
                </svg>
              </div>
              <h3 class="text-base font-bold text-gray-900 mb-3">
                {{ t('landing.features.tracking.title') }}
              </h3>
              <p class="text-gray-600 leading-relaxed">
                {{ t('landing.features.tracking.description') }}
              </p>
            </div>

            <div
              class="bg-white border border-gray-100 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow"
            >
              <div
                class="w-14 h-14 bg-secondary-100 rounded-lg flex items-center justify-center mb-4"
              >
                <svg
                  class="w-8 h-8 text-secondary-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                  />
                </svg>
              </div>
              <h3 class="text-base font-bold text-gray-900 mb-3">
                {{ t('landing.features.insights.title') }}
              </h3>
              <p class="text-gray-600 leading-relaxed">
                {{ t('landing.features.insights.description') }}
              </p>
            </div>

            <div
              class="bg-white border border-gray-100 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow"
            >
              <div
                class="w-14 h-14 bg-primary-100 rounded-lg flex items-center justify-center mb-4"
              >
                <svg
                  class="w-8 h-8 text-primary-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"
                  />
                </svg>
              </div>
              <h3 class="text-base font-bold text-gray-900 mb-3">
                {{ t('landing.features.customizable.title') }}
              </h3>
              <p class="text-gray-600 leading-relaxed">
                {{ t('landing.features.customizable.description') }}
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  </PublicLayout>
</template>
