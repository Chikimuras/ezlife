import { defineStore } from 'pinia'
import { ref } from 'vue'
import { insightsApi } from '@/lib/api/insights'
import type { DailyInsight, WeeklyInsight } from '@/lib/api/schemas/insights'
import { errorLogger } from '@/lib/errors/errorLogger'
import { useErrorHandler } from '@/composables/useErrorHandler'

export const useInsightsStore = defineStore('insights', () => {
  const dailyInsight = ref<DailyInsight | null>(null)
  const weeklyInsight = ref<WeeklyInsight | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const { handleApiError } = useErrorHandler()

  const fetchDailyComparison = async (date?: string) => {
    loading.value = true
    error.value = null
    try {
      dailyInsight.value = await insightsApi.getDailyComparison(date)
      errorLogger.logInfo('Daily insights fetched successfully', { date })
    } catch (err) {
      error.value = 'Failed to fetch daily insights'
      await handleApiError(err, 'Fetching Daily Insights')
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchWeeklyComparison = async (date?: string) => {
    loading.value = true
    error.value = null
    try {
      weeklyInsight.value = await insightsApi.getWeeklyComparison(date)
      errorLogger.logInfo('Weekly insights fetched successfully', { date })
    } catch (err) {
      error.value = 'Failed to fetch weekly insights'
      await handleApiError(err, 'Fetching Weekly Insights')
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    dailyInsight,
    weeklyInsight,
    loading,
    error,
    fetchDailyComparison,
    fetchWeeklyComparison,
  }
})
