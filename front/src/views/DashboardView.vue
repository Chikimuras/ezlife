<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import AuthenticatedLayout from '@/components/layouts/AuthenticatedLayout.vue'
import Button from '@/components/ui/Button.vue'
import TotalTimeCard from '@/components/features/dashboard/TotalTimeCard.vue'
import StatisticsCards from '@/components/features/dashboard/StatisticsCards.vue'
import TopCategoriesList from '@/components/features/dashboard/TopCategoriesList.vue'
import GroupBreakdownChart from '@/components/features/dashboard/GroupBreakdownChart.vue'
import WeeklyTotalTimeCard from '@/components/features/dashboard/WeeklyTotalTimeCard.vue'
import WeeklyStatisticsCards from '@/components/features/dashboard/WeeklyStatisticsCards.vue'
import WeeklyTopCategoriesList from '@/components/features/dashboard/WeeklyTopCategoriesList.vue'
import WeeklyGroupBreakdownChart from '@/components/features/dashboard/WeeklyGroupBreakdownChart.vue'
import { useInsightsStore } from '@/stores/insights'

const { t } = useI18n()
const insightsStore = useInsightsStore()

const savedViewMode = localStorage.getItem('dashboard-view-mode') as 'daily' | 'weekly' | null
const viewMode = ref<'daily' | 'weekly'>(savedViewMode ?? 'daily')
const selectedDate = ref(new Date())

const formattedDate = computed(() => selectedDate.value.toISOString().split('T')[0] ?? '')

onMounted(async () => {
  if (viewMode.value === 'weekly') {
    await insightsStore.fetchWeeklyComparison(formattedDate.value)
  } else {
    await insightsStore.fetchDailyComparison(formattedDate.value)
  }
})

const switchViewMode = (mode: 'daily' | 'weekly') => {
  viewMode.value = mode
  localStorage.setItem('dashboard-view-mode', mode)
  if (mode === 'weekly') {
    insightsStore.fetchWeeklyComparison(formattedDate.value)
  } else {
    insightsStore.fetchDailyComparison(formattedDate.value)
  }
}
</script>

<template>
  <AuthenticatedLayout>
    <div class="py-6 px-4">
      <div class="max-w-7xl mx-auto">
        <div class="flex items-center justify-between mb-6">
          <h1 class="text-2xl font-semibold text-gray-900">{{ t('dashboard.title') }}</h1>

          <div class="flex gap-2">
            <Button
              :variant="viewMode === 'daily' ? 'default' : 'outline'"
              size="sm"
              @click="switchViewMode('daily')"
            >
              {{ t('dashboard.viewMode.daily') }}
            </Button>
            <Button
              :variant="viewMode === 'weekly' ? 'default' : 'outline'"
              size="sm"
              @click="switchViewMode('weekly')"
            >
              {{ t('dashboard.viewMode.weekly') }}
            </Button>
          </div>
        </div>

        <div v-if="insightsStore.loading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>

        <div v-else-if="insightsStore.error" class="bg-red-50 border border-red-200 rounded-lg p-4">
          <p class="text-sm text-red-700">{{ insightsStore.error }}</p>
        </div>

        <div v-else-if="viewMode === 'daily' && insightsStore.dailyInsight" class="space-y-6">
          <TotalTimeCard :insight="insightsStore.dailyInsight" />
          <StatisticsCards :stats="insightsStore.dailyInsight.stats" />
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <TopCategoriesList :categories="insightsStore.dailyInsight.topCategories" />
            <GroupBreakdownChart :breakdown="insightsStore.dailyInsight.groupBreakdown" />
          </div>
        </div>

        <div v-else-if="viewMode === 'weekly' && insightsStore.weeklyInsight" class="space-y-6">
          <WeeklyTotalTimeCard :insight="insightsStore.weeklyInsight" />
          <WeeklyStatisticsCards :stats="insightsStore.weeklyInsight.stats" />
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <WeeklyTopCategoriesList :categories="insightsStore.weeklyInsight.topCategories" />
            <WeeklyGroupBreakdownChart :breakdown="insightsStore.weeklyInsight.groupBreakdown" />
          </div>
        </div>
      </div>
    </div>
  </AuthenticatedLayout>
</template>
