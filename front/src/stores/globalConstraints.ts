import { defineStore } from 'pinia'
import { ref } from 'vue'
import { globalConstraintsApi } from '@/lib/api/globalConstraints'
import type {
  GlobalConstraints,
  UpdateGlobalConstraints,
} from '@/lib/api/schemas/globalConstraints'
import { errorLogger } from '@/lib/errors/errorLogger'
import { useErrorHandler } from '@/composables/useErrorHandler'

export const useGlobalConstraintsStore = defineStore('globalConstraints', () => {
  const constraints = ref<GlobalConstraints | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const { handleApiError } = useErrorHandler()

  const fetchConstraints = async () => {
    loading.value = true
    error.value = null
    try {
      constraints.value = await globalConstraintsApi.get()
      errorLogger.logInfo('Global constraints fetched successfully')
    } catch (err) {
      error.value = 'Failed to fetch constraints'
      await handleApiError(err, 'Fetching Global Constraints')
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateConstraints = async (data: UpdateGlobalConstraints) => {
    loading.value = true
    error.value = null
    try {
      constraints.value = await globalConstraintsApi.update(data)
      errorLogger.logInfo('Global constraints updated successfully')
      return constraints.value
    } catch (err) {
      error.value = 'Failed to update constraints'
      await handleApiError(err, 'Updating Global Constraints')
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    constraints,
    loading,
    error,
    fetchConstraints,
    updateConstraints,
  }
})
