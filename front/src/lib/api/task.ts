import { z } from 'zod'

import { api, fetcher } from './client'
import {
  TaskListSchema,
  CreateTaskListSchema,
  UpdateTaskListSchema,
  TaskSchema,
  CreateTaskSchema,
  UpdateTaskSchema,
  TaskCompleteSchema,
  ConvertToActivitySchema,
  TaskActivitySchema,
  type TaskList,
  type CreateTaskList,
  type UpdateTaskList,
  type Task,
  type CreateTask,
  type UpdateTask,
  type TaskComplete,
  type ConvertToActivity,
  type TaskActivity,
} from './schemas/task'

export const taskListApi = {
  async getAll(): Promise<TaskList[]> {
    return fetcher(api.get('api/v1/task-lists'), TaskListSchema.array())
  },

  async create(data: CreateTaskList): Promise<TaskList> {
    const validated = CreateTaskListSchema.parse(data)
    return fetcher(api.post('api/v1/task-lists', { json: validated }), TaskListSchema)
  },

  async update(id: string, data: UpdateTaskList): Promise<TaskList> {
    const validated = UpdateTaskListSchema.parse(data)
    return fetcher(api.put(`api/v1/task-lists/${id}`, { json: validated }), TaskListSchema)
  },

  async delete(id: string): Promise<void> {
    await api.delete(`api/v1/task-lists/${id}`)
  },
}

export const taskApi = {
  async getAll(params?: { listId?: string; status?: string }): Promise<Task[]> {
    const searchParams: Record<string, string> = {}
    if (params?.listId) searchParams.list_id = params.listId
    if (params?.status) searchParams.status = params.status
    return fetcher(api.get('api/v1/tasks', { searchParams }), TaskSchema.array())
  },

  async getById(id: string): Promise<Task> {
    return fetcher(api.get(`api/v1/tasks/${id}`), TaskSchema)
  },

  async create(data: CreateTask): Promise<Task> {
    const validated = CreateTaskSchema.parse(data)
    return fetcher(api.post('api/v1/tasks', { json: validated }), TaskSchema)
  },

  async update(id: string, data: UpdateTask): Promise<Task> {
    const validated = UpdateTaskSchema.parse(data)
    return fetcher(api.put(`api/v1/tasks/${id}`, { json: validated }), TaskSchema)
  },

  async delete(id: string): Promise<void> {
    await api.delete(`api/v1/tasks/${id}`)
  },

  async complete(id: string, data: TaskComplete): Promise<Task> {
    const validated = TaskCompleteSchema.parse(data)
    return fetcher(api.post(`api/v1/tasks/${id}/complete`, { json: validated }), TaskSchema)
  },

  async convertToActivity(id: string, data: ConvertToActivity): Promise<TaskActivity> {
    const validated = ConvertToActivitySchema.parse(data)
    return fetcher(
      api.post(`api/v1/tasks/${id}/convert-to-activity`, { json: validated }),
      TaskActivitySchema,
    )
  },

  async generateOccurrences(id: string, count: number = 10): Promise<Task[]> {
    return fetcher(
      api.post(`api/v1/tasks/${id}/generate-occurrences`, {
        searchParams: { count: count.toString() },
      }),
      TaskSchema.array(),
    )
  },

  async generateRolling(): Promise<{ createdCount: number; recurringTasksChecked: number }> {
    return fetcher(
      api.post('api/v1/tasks/generate-rolling'),
      z.object({ createdCount: z.number(), recurringTasksChecked: z.number() }),
    )
  },
}
