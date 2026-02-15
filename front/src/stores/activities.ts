import { defineStore } from 'pinia'
import { ref } from 'vue'
import { activityApi } from '@/lib/api/activity'
import type { Activity, CreateActivity, UpdateActivity } from '@/lib/api/schemas/activity'
import { errorLogger } from '@/lib/errors/errorLogger'
import { useErrorHandler } from '@/composables/useErrorHandler'

export const useActivitiesStore = defineStore('activities', () => {
  const activities = ref<Activity[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const { handleApiError } = useErrorHandler()

  const fetchActivities = async () => {
    loading.value = true
    error.value = null
    try {
      activities.value = await activityApi.getAll()
      errorLogger.logInfo('Activities fetched successfully', { count: activities.value.length })
    } catch (err) {
      error.value = 'Failed to fetch activities'
      await handleApiError(err, 'Fetching Activities')
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchActivitiesByDate = async (date: string) => {
    loading.value = true
    error.value = null
    try {
      activities.value = await activityApi.getByDate(date)
      errorLogger.logInfo('Activities fetched by date', { date, count: activities.value.length })
    } catch (err) {
      error.value = 'Failed to fetch activities'
      await handleApiError(err, 'Fetching Activities by Date')
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchActivitiesByDateRange = async (dates: string[]) => {
    loading.value = true
    error.value = null
    try {
      const results = await Promise.all(dates.map((date) => activityApi.getByDate(date)))
      // Flatten all activities from all dates into a single array
      activities.value = results.flat()
      errorLogger.logInfo('Activities fetched by date range', {
        dateCount: dates.length,
        activityCount: activities.value.length,
      })
    } catch (err) {
      error.value = 'Failed to fetch activities'
      await handleApiError(err, 'Fetching Activities by Date Range')
      throw err
    } finally {
      loading.value = false
    }
  }

  const createActivity = async (data: CreateActivity) => {
    loading.value = true
    error.value = null
    try {
      const newActivity = await activityApi.create(data)
      activities.value.push(newActivity)
      errorLogger.logInfo('Activity created successfully', { activityId: newActivity.id })
      return newActivity
    } catch (err) {
      error.value = 'Failed to create activity'
      await handleApiError(err, 'Creating Activity')
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateActivity = async (id: string, data: UpdateActivity) => {
    loading.value = true
    error.value = null
    try {
      const updated = await activityApi.update(id, data)
      const index = activities.value.findIndex((a) => a.id === id)
      if (index !== -1) {
        activities.value[index] = updated
      }
      errorLogger.logInfo('Activity updated successfully', { activityId: id })
      return updated
    } catch (err) {
      error.value = 'Failed to update activity'
      await handleApiError(err, 'Updating Activity')
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteActivity = async (id: string) => {
    loading.value = true
    error.value = null
    try {
      await activityApi.delete(id)
      activities.value = activities.value.filter((a) => a.id !== id)
      errorLogger.logInfo('Activity deleted successfully', { activityId: id })
    } catch (err) {
      error.value = 'Failed to delete activity'
      await handleApiError(err, 'Deleting Activity')
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    activities,
    loading,
    error,
    fetchActivities,
    fetchActivitiesByDate,
    fetchActivitiesByDateRange,
    createActivity,
    updateActivity,
    deleteActivity,
  }
})
