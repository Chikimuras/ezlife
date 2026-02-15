<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { TopCategoryItem } from '@/lib/api/schemas/insights'
import { ArrowUp, ArrowDown, Minus } from 'lucide-vue-next'

const props = defineProps<{
  categories: TopCategoryItem[]
}>()

const { t } = useI18n()

const formatTime = (minutes: number) => {
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`
}

const getDeltaColor = (delta: number) => {
  if (delta > 0) return 'text-green-700'
  if (delta < 0) return 'text-red-700'
  return 'text-gray-500'
}

const getDeltaBgColor = (delta: number) => {
  if (delta > 0) return 'bg-green-100'
  if (delta < 0) return 'bg-red-100'
  return 'bg-gray-100'
}
</script>

<template>
  <div class="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
    <h2 class="text-lg font-semibold text-gray-900 mb-4">
      {{ t('dashboard.topCategories.title') }}
    </h2>

    <div class="space-y-3">
      <div
        v-for="(category, index) in categories"
        :key="category.categoryId"
        class="flex items-center justify-between p-3 rounded-lg border border-gray-100 hover:bg-gray-50 transition-colors"
      >
        <!-- Left: Rank + Category Info -->
        <div class="flex items-center gap-3 flex-1">
          <div
            class="flex items-center justify-center w-6 h-6 rounded-full bg-primary-100 text-primary-700 text-xs font-semibold"
          >
            {{ index + 1 }}
          </div>

          <div class="flex flex-col">
            <span class="text-sm font-medium text-gray-900">{{ category.categoryName }}</span>
            <div class="flex items-center gap-2 mt-0.5">
              <div
                v-if="category.groupColor"
                class="w-2 h-2 rounded-full"
                :style="{ backgroundColor: category.groupColor }"
              ></div>
              <span class="text-xs text-gray-500">{{ category.groupName }}</span>
            </div>
          </div>
        </div>

        <!-- Right: Time + Delta -->
        <div class="flex items-center gap-3">
          <div class="text-right">
            <div class="text-sm font-semibold text-gray-900">
              {{ formatTime(category.minutes) }}
            </div>
            <div class="text-xs text-gray-500">{{ category.percentOfTotal.toFixed(0) }}%</div>
          </div>

          <!-- Delta Badge -->
          <div
            :class="[
              'flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold',
              getDeltaBgColor(category.minutesDelta),
              getDeltaColor(category.minutesDelta),
            ]"
          >
            <ArrowUp v-if="category.minutesDelta > 0" :size="12" />
            <ArrowDown v-else-if="category.minutesDelta < 0" :size="12" />
            <Minus v-else :size="12" />
            <span>
              {{ category.minutesDelta !== 0 ? Math.abs(category.percentChange).toFixed(0) : '0' }}%
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="categories.length === 0" class="text-center py-8 text-gray-500 text-sm">
      {{ t('dashboard.topCategories.empty') }}
    </div>
  </div>
</template>
