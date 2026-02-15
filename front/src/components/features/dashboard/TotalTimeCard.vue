<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { DailyInsight } from '@/lib/api/schemas/insights'
import { ArrowUp, ArrowDown, Clock } from 'lucide-vue-next'

const props = defineProps<{
  insight: DailyInsight
}>()

const { t } = useI18n()

const totalHours = computed(() => Math.floor(props.insight.totalMinutes / 60))
const totalMinutesRemainder = computed(() => props.insight.totalMinutes % 60)

const previousHours = computed(() => Math.floor(props.insight.previousTotalMinutes / 60))
const previousMinutesRemainder = computed(() => props.insight.previousTotalMinutes % 60)

const isPositiveChange = computed(() => props.insight.totalMinutesDelta >= 0)
const deltaHours = computed(() => Math.floor(Math.abs(props.insight.totalMinutesDelta) / 60))
const deltaMinutes = computed(() => Math.abs(props.insight.totalMinutesDelta) % 60)
</script>

<template>
  <div class="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-semibold text-gray-900">{{ t('dashboard.totalTime.title') }}</h2>
      <Clock :size="24" class="text-primary-600" />
    </div>

    <!-- Today's Total -->
    <div class="mb-4">
      <div class="text-4xl font-bold text-gray-900">
        {{ totalHours }}h {{ totalMinutesRemainder }}m
      </div>
      <p class="text-sm text-gray-600 mt-1">{{ t('dashboard.totalTime.today') }}</p>
    </div>

    <!-- Comparison with Yesterday -->
    <div class="flex items-center gap-2 pt-4 border-t border-gray-100">
      <div
        :class="[
          'flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold',
          isPositiveChange ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700',
        ]"
      >
        <ArrowUp v-if="isPositiveChange" :size="14" />
        <ArrowDown v-else :size="14" />
        <span>{{ Math.abs(insight.totalMinutesPercentChange).toFixed(1) }}%</span>
      </div>

      <span class="text-sm text-gray-600">
        <template v-if="deltaHours > 0 || deltaMinutes > 0">
          {{ isPositiveChange ? '+' : '-' }}{{ deltaHours }}h {{ deltaMinutes }}m
        </template>
        <template v-else>
          {{ t('dashboard.totalTime.noChange') }}
        </template>
        {{ t('dashboard.totalTime.vsYesterday') }}
      </span>
    </div>

    <!-- Yesterday's Total (small) -->
    <div class="mt-3 text-xs text-gray-500">
      {{ t('dashboard.totalTime.yesterday') }}: {{ previousHours }}h {{ previousMinutesRemainder }}m
    </div>
  </div>
</template>
