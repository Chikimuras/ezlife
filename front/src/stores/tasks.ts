import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { taskListApi, taskApi } from '@/lib/api/task'
import type {
  TaskList,
  CreateTaskList,
  UpdateTaskList,
  Task,
  CreateTask,
  UpdateTask,
  TaskComplete,
  ConvertToActivity,
} from '@/lib/api/schemas/task'
import { errorLogger } from '@/lib/errors/errorLogger'
import { useErrorHandler } from '@/composables/useErrorHandler'

export type TaskView = 'today' | 'week' | 'all'

export const useTasksStore = defineStore('tasks', () => {
  const taskLists = ref<TaskList[]>([])
  const tasks = ref<Task[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const activeListId = ref<string | null>(null)
  const activeView = ref<TaskView>('today')

  const { handleApiError } = useErrorHandler()

  const activeList = computed(() =>
    taskLists.value.find((l) => l.id === activeListId.value) ?? null,
  )

  const getTodayString = () => new Date().toISOString().split('T')[0]!

  const getWeekBoundaries = () => {
    const today = new Date()
    const dayOfWeek = today.getDay()
    const mondayOffset = dayOfWeek === 0 ? -6 : 1 - dayOfWeek
    const sundayOffset = dayOfWeek === 0 ? 0 : 7 - dayOfWeek

    const monday = new Date(today)
    monday.setDate(today.getDate() + mondayOffset)
    const sunday = new Date(today)
    sunday.setDate(today.getDate() + sundayOffset)

    return {
      start: monday.toISOString().split('T')[0]!,
      end: sunday.toISOString().split('T')[0]!,
    }
  }

  const tasksByView = computed(() => {
    const today = getTodayString()
    const week = getWeekBoundaries()

    switch (activeView.value) {
      case 'today':
        return tasks.value.filter(
          (t) => !t.scheduledDate || t.scheduledDate === today,
        )
      case 'week':
        return tasks.value.filter(
          (t) =>
            !t.scheduledDate ||
            (t.scheduledDate >= week.start && t.scheduledDate <= week.end),
        )
      case 'all':
      default:
        return tasks.value
    }
  })

  const filteredTasks = computed(() => {
    if (!activeListId.value) return tasksByView.value
    return tasksByView.value.filter((t) => t.taskListId === activeListId.value)
  })

  const todoTasks = computed(() => filteredTasks.value.filter((t) => t.status === 'todo'))
  const inProgressTasks = computed(() =>
    filteredTasks.value.filter((t) => t.status === 'in_progress'),
  )
  const doneTasks = computed(() => filteredTasks.value.filter((t) => t.status === 'done'))

  const fetchTaskLists = async () => {
    loading.value = true
    error.value = null
    try {
      taskLists.value = await taskListApi.getAll()
      errorLogger.logInfo('Task lists fetched', { count: taskLists.value.length })
    } catch (err) {
      error.value = 'Failed to fetch task lists'
      await handleApiError(err, 'Fetching Task Lists')
      throw err
    } finally {
      loading.value = false
    }
  }

  const createTaskList = async (data: CreateTaskList) => {
    loading.value = true
    error.value = null
    try {
      const created = await taskListApi.create(data)
      taskLists.value.push(created)
      errorLogger.logInfo('Task list created', { id: created.id })
      return created
    } catch (err) {
      error.value = 'Failed to create task list'
      await handleApiError(err, 'Creating Task List')
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateTaskList = async (id: string, data: UpdateTaskList) => {
    loading.value = true
    error.value = null
    try {
      const updated = await taskListApi.update(id, data)
      const index = taskLists.value.findIndex((l) => l.id === id)
      if (index !== -1) taskLists.value[index] = updated
      errorLogger.logInfo('Task list updated', { id })
      return updated
    } catch (err) {
      error.value = 'Failed to update task list'
      await handleApiError(err, 'Updating Task List')
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteTaskList = async (id: string) => {
    loading.value = true
    error.value = null
    try {
      await taskListApi.delete(id)
      taskLists.value = taskLists.value.filter((l) => l.id !== id)
      if (activeListId.value === id) activeListId.value = null
      errorLogger.logInfo('Task list deleted', { id })
    } catch (err) {
      error.value = 'Failed to delete task list'
      await handleApiError(err, 'Deleting Task List')
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchTasks = async (listId?: string, status?: string) => {
    loading.value = true
    error.value = null
    try {
      tasks.value = await taskApi.getAll({ listId, status })
      errorLogger.logInfo('Tasks fetched', { count: tasks.value.length })
    } catch (err) {
      error.value = 'Failed to fetch tasks'
      await handleApiError(err, 'Fetching Tasks')
      throw err
    } finally {
      loading.value = false
    }
  }

  const createTask = async (data: CreateTask) => {
    loading.value = true
    error.value = null
    try {
      const created = await taskApi.create(data)
      tasks.value.push(created)
      errorLogger.logInfo('Task created', { id: created.id })
      return created
    } catch (err) {
      error.value = 'Failed to create task'
      await handleApiError(err, 'Creating Task')
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateTask = async (id: string, data: UpdateTask) => {
    loading.value = true
    error.value = null
    try {
      const updated = await taskApi.update(id, data)
      const index = tasks.value.findIndex((t) => t.id === id)
      if (index !== -1) tasks.value[index] = updated
      errorLogger.logInfo('Task updated', { id })
      return updated
    } catch (err) {
      error.value = 'Failed to update task'
      await handleApiError(err, 'Updating Task')
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteTask = async (id: string) => {
    loading.value = true
    error.value = null
    try {
      await taskApi.delete(id)
      tasks.value = tasks.value.filter((t) => t.id !== id)
      errorLogger.logInfo('Task deleted', { id })
    } catch (err) {
      error.value = 'Failed to delete task'
      await handleApiError(err, 'Deleting Task')
      throw err
    } finally {
      loading.value = false
    }
  }

  const completeTask = async (id: string, data: TaskComplete) => {
    loading.value = true
    error.value = null
    try {
      const updated = await taskApi.complete(id, data)
      const index = tasks.value.findIndex((t) => t.id === id)
      if (index !== -1) tasks.value[index] = updated
      errorLogger.logInfo('Task completed', { id, addedToTracker: data.addToTracker })
      return updated
    } catch (err) {
      error.value = 'Failed to complete task'
      await handleApiError(err, 'Completing Task')
      throw err
    } finally {
      loading.value = false
    }
  }

  const convertToActivity = async (id: string, data: ConvertToActivity) => {
    loading.value = true
    error.value = null
    try {
      const taskActivity = await taskApi.convertToActivity(id, data)
      const task = tasks.value.find((t) => t.id === id)
      if (task) {
        task.status = 'done'
        task.activityIds.push(taskActivity.activityId)
      }
      errorLogger.logInfo('Task converted to activity', { taskId: id })
      return taskActivity
    } catch (err) {
      error.value = 'Failed to convert task to activity'
      await handleApiError(err, 'Converting Task to Activity')
      throw err
    } finally {
      loading.value = false
    }
  }

  const generateOccurrences = async (id: string, count: number = 10) => {
    loading.value = true
    error.value = null
    try {
      const newTasks = await taskApi.generateOccurrences(id, count)
      tasks.value.push(...newTasks)
      errorLogger.logInfo('Task occurrences generated', { id, count, created: newTasks.length })
      return newTasks
    } catch (err) {
      error.value = 'Failed to generate occurrences'
      await handleApiError(err, 'Generating Occurrences')
      throw err
    } finally {
      loading.value = false
    }
  }

  const setActiveList = (id: string | null) => {
    activeListId.value = id
  }

  const setActiveView = (view: TaskView) => {
    activeView.value = view
  }

  return {
    taskLists,
    tasks,
    loading,
    error,
    activeListId,
    activeView,
    activeList,
    filteredTasks,
    todoTasks,
    inProgressTasks,
    doneTasks,
    fetchTaskLists,
    createTaskList,
    updateTaskList,
    deleteTaskList,
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    completeTask,
    convertToActivity,
    generateOccurrences,
    setActiveList,
    setActiveView,
  }
})
