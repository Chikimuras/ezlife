import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { timerApi } from '@/lib/api/timer'
import type { Activity } from '@/lib/api/schemas/activity'
import { useErrorHandler } from '@/composables/useErrorHandler'
import { errorLogger } from '@/lib/errors/errorLogger'

export const useTimerStore = defineStore('timer', () => {
  const activeActivity = ref<Activity | null>(null)
  const isRunning = ref(false)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const intervalId = ref<ReturnType<typeof setInterval> | null>(null)
  const currentElapsed = ref(0)

  const { handleApiError } = useErrorHandler()

  const elapsedFormatted = computed(() => {
    const seconds = currentElapsed.value
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60

    const padZero = (num: number): string => String(num).padStart(2, '0')

    return `${padZero(hours)}:${padZero(minutes)}:${padZero(secs)}`
  })

  const categoryId = computed(() => activeActivity.value?.categoryId ?? null)

  const startTimer = async (categoryId: string): Promise<void> => {
    loading.value = true
    error.value = null
    try {
      const activity = await timerApi.start(categoryId)
      activeActivity.value = activity
      isRunning.value = true
      _startTicking()
      errorLogger.logInfo('Timer started', { categoryId, activityId: activity.id })
    } catch (err) {
      error.value = 'Failed to start timer'
      await handleApiError(err, 'Starting Timer')
      throw err
    } finally {
      loading.value = false
    }
  }

  const stopTimer = async (): Promise<void> => {
    loading.value = true
    error.value = null
    try {
      await timerApi.stop()
      _stopTicking()
      isRunning.value = false
      activeActivity.value = null
      currentElapsed.value = 0
      errorLogger.logInfo('Timer stopped')
    } catch (err) {
      error.value = 'Failed to stop timer'
      await handleApiError(err, 'Stopping Timer')
      throw err
    } finally {
      loading.value = false
    }
  }

  const stopTimerAt = async (endTime: string): Promise<void> => {
    loading.value = true
    error.value = null
    try {
      await timerApi.stopAt(endTime)
      _stopTicking()
      isRunning.value = false
      activeActivity.value = null
      currentElapsed.value = 0
      errorLogger.logInfo('Timer stopped at', { endTime })
    } catch (err) {
      error.value = 'Failed to stop timer'
      await handleApiError(err, 'Stopping Timer at Time')
      throw err
    } finally {
      loading.value = false
    }
  }

  const checkActiveTimer = async (): Promise<Activity | null> => {
    try {
      const activity = await timerApi.getActive()
      if (activity) {
        activeActivity.value = activity
        isRunning.value = true
        _startTicking()
        errorLogger.logInfo('Active timer found', { activityId: activity.id })
      } else {
        isRunning.value = false
      }
      return activity
    } catch (err) {
      await handleApiError(err, 'Checking Active Timer')
      throw err
    }
  }

  const clearTimer = (): void => {
    _stopTicking()
    activeActivity.value = null
    isRunning.value = false
    loading.value = false
    error.value = null
    currentElapsed.value = 0
  }

  const _startTicking = (): void => {
    _stopTicking()

    if (!activeActivity.value) {
      return
    }

    const { date, startTime } = activeActivity.value
    const dateParts = date.split('-').map(Number)
    const timeParts = startTime.split(':').map(Number)

    const year = dateParts[0] ?? 2024
    const month = dateParts[1] ?? 1
    const day = dateParts[2] ?? 1
    const hours = timeParts[0] ?? 0
    const minutes = timeParts[1] ?? 0

    const startDate = new Date(year, month - 1, day, hours, minutes, 0, 0)
    const now = new Date()

    currentElapsed.value = Math.floor((now.getTime() - startDate.getTime()) / 1000)

    intervalId.value = setInterval(() => {
      currentElapsed.value++
    }, 1000)
  }

  const _stopTicking = (): void => {
    if (intervalId.value) {
      clearInterval(intervalId.value)
    }
    intervalId.value = null
  }

  return {
    activeActivity,
    isRunning,
    loading,
    error,
    currentElapsed,
    elapsedFormatted,
    categoryId,
    startTimer,
    stopTimer,
    stopTimerAt,
    checkActiveTimer,
    clearTimer,
  }
})
