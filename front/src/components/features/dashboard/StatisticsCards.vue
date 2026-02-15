<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { DailyStats } from '@/lib/api/schemas/insights'
import { Activity, TrendingUp, Clock, Timer } from 'lucide-vue-next'

const props = defineProps<{
  stats: DailyStats
}>()

const { t } = useI18n()

const formatTime = (minutes: number) => {
  // Round to nearest minute for cleaner display
  const roundedMinutes = Math.round(minutes)
  const hours = Math.floor(roundedMinutes / 60)
  const mins = roundedMinutes % 60

  if (hours > 0) {
    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`
  }
  return `${mins}m`
}

const getDeltaBadge = (delta: number) => {
  if (delta > 0) return { text: `+${delta}`, class: 'bg-green-100 text-green-700' }
  if (delta < 0) return { text: `${delta}`, class: 'bg-red-100 text-red-700' }
  return { text: '0', class: 'bg-gray-100 text-gray-600' }
}
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
    <!-- Activities Count -->
    <div class="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
      <div class="flex items-center justify-between mb-3">
        <span class="text-sm font-medium text-gray-600">
          {{ t('dashboard.stats.activitiesCount') }}
        </span>
        <Activity :size="20" class="text-primary-600" />
      </div>
      <div class="flex items-baseline gap-2">
        <span class="text-3xl font-bold text-gray-900">{{ stats.activitiesCount }}</span>
        <span
          :class="[
            'px-2 py-0.5 rounded-full text-xs font-semibold',
            getDeltaBadge(stats.activitiesCountDelta).class,
          ]"
        >
          {{ getDeltaBadge(stats.activitiesCountDelta).text }}
        </span>
      </div>
    </div>

    <!-- Categories Used -->
    <div class="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
      <div class="flex items-center justify-between mb-3">
        <span class="text-sm font-medium text-gray-600">
          {{ t('dashboard.stats.categoriesUsed') }}
        </span>
        <TrendingUp :size="20" class="text-secondary-600" />
      </div>
      <div class="flex items-baseline gap-2">
        <span class="text-3xl font-bold text-gray-900">{{ stats.categoriesUsed }}</span>
        <span
          :class="[
            'px-2 py-0.5 rounded-full text-xs font-semibold',
            getDeltaBadge(stats.categoriesUsedDelta).class,
          ]"
        >
          {{ getDeltaBadge(stats.categoriesUsedDelta).text }}
        </span>
      </div>
    </div>

    <!-- Average Duration -->
    <div class="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
      <div class="flex items-center justify-between mb-3">
        <span class="text-sm font-medium text-gray-600">
          {{ t('dashboard.stats.avgDuration') }}
        </span>
        <Clock :size="20" class="text-primary-600" />
      </div>
      <div class="flex items-baseline gap-2">
        <span class="text-2xl font-bold text-gray-900">
          {{ formatTime(stats.averageActivityDuration) }}
        </span>
      </div>
    </div>

    <!-- Longest Activity -->
    <div class="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
      <div class="flex items-center justify-between mb-3">
        <span class="text-sm font-medium text-gray-600">
          {{ t('dashboard.stats.longestActivity') }}
        </span>
        <Timer :size="20" class="text-secondary-600" />
      </div>
      <div v-if="stats.longestActivity">
        <div class="text-2xl font-bold text-gray-900">
          {{ formatTime(stats.longestActivity.minutes) }}
        </div>
        <div class="text-xs text-gray-500 mt-1">
          {{ stats.longestActivity.categoryName }}
        </div>
      </div>
      <div v-else class="text-sm text-gray-400">{{ t('dashboard.stats.noData') }}</div>
    </div>
  </div>
</template>
