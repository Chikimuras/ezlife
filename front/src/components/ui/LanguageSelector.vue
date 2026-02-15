<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { availableLocales } from '@/lib/i18n'

const { locale } = useI18n()

const changeLocale = (code: string) => {
  locale.value = code
  localStorage.setItem('locale', code)
}
</script>

<template>
  <div class="relative inline-block">
    <select
      v-model="locale"
      @change="(e) => changeLocale((e.target as HTMLSelectElement).value)"
      class="appearance-none bg-white border border-gray-200 rounded-lg px-4 py-2 pr-8 text-sm font-medium text-gray-700 hover:border-primary-300 focus:outline-none focus:ring-2 focus:ring-primary-400 focus:border-transparent transition-colors cursor-pointer"
    >
      <option v-for="loc in availableLocales" :key="loc.code" :value="loc.code">
        {{ loc.flag }} {{ loc.name }}
      </option>
    </select>
    <div
      class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-500"
    >
      <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </div>
  </div>
</template>
