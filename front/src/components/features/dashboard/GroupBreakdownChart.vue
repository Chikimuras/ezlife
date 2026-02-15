<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { GroupBreakdownItem } from '@/lib/api/schemas/insights'

const props = defineProps<{
  breakdown: GroupBreakdownItem[]
}>()

const { t } = useI18n()

const sortedBreakdown = computed(() => [...props.breakdown].sort((a, b) => b.minutes - a.minutes))

const formatTime = (minutes: number) => {
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  return `${hours}h ${mins}m`
}
</script>

<template>
  <div class="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
    <h2 class="text-lg font-semibold text-gray-900 mb-4">
      {{ t('dashboard.groupBreakdown.title') }}
    </h2>

    <!-- Visual Bar Chart -->
    <div class="mb-6">
      <div class="flex h-8 rounded-lg overflow-hidden">
        <div
          v-for="item in sortedBreakdown"
          :key="item.groupId"
          :style="{
            width: `${item.percentOfTotal}%`,
            backgroundColor: item.groupColor || '#9ca3af',
          }"
          class="transition-all hover:opacity-80"
          :title="`${item.groupName}: ${formatTime(item.minutes)}`"
        ></div>
      </div>
    </div>

    <!-- Legend / Details -->
    <div class="space-y-3">
      <div
        v-for="item in sortedBreakdown"
        :key="item.groupId"
        class="flex items-center justify-between"
      >
        <div class="flex items-center gap-2 flex-1">
          <div
            class="w-3 h-3 rounded-full"
            :style="{ backgroundColor: item.groupColor || '#9ca3af' }"
          ></div>
          <span class="text-sm font-medium text-gray-900">{{ item.groupName }}</span>
        </div>

        <div class="flex items-center gap-4">
          <span class="text-sm text-gray-900 font-semibold">{{ formatTime(item.minutes) }}</span>
          <span class="text-xs text-gray-500 w-12 text-right">
            {{ item.percentOfTotal.toFixed(0) }}%
          </span>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="breakdown.length === 0" class="text-center py-8 text-gray-500 text-sm">
      {{ t('dashboard.groupBreakdown.empty') }}
    </div>
  </div>
</template>
