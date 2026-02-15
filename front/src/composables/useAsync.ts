import { ref, type Ref } from 'vue'
import { useErrorHandler } from './useErrorHandler'
import type { AppError } from '@/lib/errors/AppError'

export interface UseAsyncState<T> {
  data: Ref<T | null>
  error: Ref<AppError | null>
  loading: Ref<boolean>
  execute: (...args: any[]) => Promise<T | null>
  reset: () => void
}

export function useAsync<T>(
  asyncFn: (...args: any[]) => Promise<T>,
  options: {
    immediate?: boolean
    showErrorNotification?: boolean
    errorContext?: string
  } = {},
): UseAsyncState<T> {
  const { immediate = false, showErrorNotification = true, errorContext } = options

  const { handleError } = useErrorHandler()

  const data = ref<T | null>(null) as Ref<T | null>
  const error = ref<AppError | null>(null) as Ref<AppError | null>
  const loading = ref(false)

  const execute = async (...args: any[]): Promise<T | null> => {
    loading.value = true
    error.value = null

    try {
      const result = await asyncFn(...args)
      data.value = result
      return result
    } catch (err) {
      const appError = await handleError(err, {
        showNotification: showErrorNotification,
        context: errorContext,
      })
      error.value = appError
      return null
    } finally {
      loading.value = false
    }
  }

  const reset = () => {
    data.value = null
    error.value = null
    loading.value = false
  }

  if (immediate) {
    execute()
  }

  return {
    data,
    error,
    loading,
    execute,
    reset,
  }
}
