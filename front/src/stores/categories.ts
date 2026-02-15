import { defineStore } from 'pinia'
import { ref } from 'vue'
import { categoryApi } from '@/lib/api/category'
import type { Category, CreateCategory, UpdateCategory } from '@/lib/api/schemas/category'
import { errorLogger } from '@/lib/errors/errorLogger'
import { useErrorHandler } from '@/composables/useErrorHandler'

export const useCategoriesStore = defineStore('categories', () => {
  const categories = ref<Category[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const { handleApiError } = useErrorHandler()

  const fetchCategories = async () => {
    loading.value = true
    error.value = null
    try {
      categories.value = await categoryApi.getAll()
      errorLogger.logInfo('Categories fetched successfully', { count: categories.value.length })
    } catch (err) {
      error.value = 'Failed to fetch categories'
      await handleApiError(err, 'Fetching Categories')
      throw err
    } finally {
      loading.value = false
    }
  }

  const createCategory = async (data: CreateCategory) => {
    loading.value = true
    error.value = null
    try {
      const newCategory = await categoryApi.create(data)
      categories.value.push(newCategory)
      errorLogger.logInfo('Category created successfully', { categoryId: newCategory.id })
      return newCategory
    } catch (err) {
      error.value = 'Failed to create category'
      await handleApiError(err, 'Creating Category')
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateCategory = async (id: string, data: UpdateCategory) => {
    loading.value = true
    error.value = null
    try {
      const updated = await categoryApi.update(id, data)
      const index = categories.value.findIndex((c) => c.id === id)
      if (index !== -1) {
        categories.value[index] = updated
      }
      errorLogger.logInfo('Category updated successfully', { categoryId: id })
      return updated
    } catch (err) {
      error.value = 'Failed to update category'
      await handleApiError(err, 'Updating Category')
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteCategory = async (id: string) => {
    loading.value = true
    error.value = null
    try {
      await categoryApi.delete(id)
      categories.value = categories.value.filter((c) => c.id !== id)
      errorLogger.logInfo('Category deleted successfully', { categoryId: id })
    } catch (err) {
      error.value = 'Failed to delete category'
      await handleApiError(err, 'Deleting Category')
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    categories,
    loading,
    error,
    fetchCategories,
    createCategory,
    updateCategory,
    deleteCategory,
  }
})
