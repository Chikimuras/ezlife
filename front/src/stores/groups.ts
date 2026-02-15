import { defineStore } from 'pinia'
import { ref } from 'vue'
import { groupApi } from '@/lib/api/group'
import type { Group, CreateGroup, UpdateGroup } from '@/lib/api/schemas/group'
import { errorLogger } from '@/lib/errors/errorLogger'
import { useErrorHandler } from '@/composables/useErrorHandler'

export const useGroupsStore = defineStore('groups', () => {
  const groups = ref<Group[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const { handleApiError } = useErrorHandler()

  const fetchGroups = async () => {
    loading.value = true
    error.value = null
    try {
      groups.value = await groupApi.getAll()
      errorLogger.logInfo('Groups fetched successfully', { count: groups.value.length })
    } catch (err) {
      error.value = 'Failed to fetch groups'
      await handleApiError(err, 'Fetching Groups')
      throw err
    } finally {
      loading.value = false
    }
  }

  const createGroup = async (data: CreateGroup) => {
    loading.value = true
    error.value = null
    try {
      const newGroup = await groupApi.create(data)
      groups.value.push(newGroup)
      errorLogger.logInfo('Group created successfully', { groupId: newGroup.id })
      return newGroup
    } catch (err) {
      error.value = 'Failed to create group'
      await handleApiError(err, 'Creating Group')
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateGroup = async (id: string, data: UpdateGroup) => {
    loading.value = true
    error.value = null
    try {
      const updated = await groupApi.update(id, data)
      const index = groups.value.findIndex((g) => g.id === id)
      if (index !== -1) {
        groups.value[index] = updated
      }
      errorLogger.logInfo('Group updated successfully', { groupId: id })
      return updated
    } catch (err) {
      error.value = 'Failed to update group'
      await handleApiError(err, 'Updating Group')
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteGroup = async (id: string) => {
    loading.value = true
    error.value = null
    try {
      await groupApi.delete(id)
      groups.value = groups.value.filter((g) => g.id !== id)
      errorLogger.logInfo('Group deleted successfully', { groupId: id })
    } catch (err) {
      error.value = 'Failed to delete group'
      await handleApiError(err, 'Deleting Group')
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    groups,
    loading,
    error,
    fetchGroups,
    createGroup,
    updateGroup,
    deleteGroup,
  }
})
