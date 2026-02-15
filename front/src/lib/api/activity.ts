import { api, fetcher } from './client'
import {
  ActivitySchema,
  CreateActivitySchema,
  UpdateActivitySchema,
  type Activity,
  type CreateActivity,
  type UpdateActivity,
} from './schemas/activity'

export const activityApi = {
  async getAll(): Promise<Activity[]> {
    return fetcher(api.get('api/v1/activities'), ActivitySchema.array())
  },

  async getByDate(date: string): Promise<Activity[]> {
    return fetcher(api.get(`api/v1/activities/date/${date}`), ActivitySchema.array())
  },

  async getById(id: string): Promise<Activity> {
    return fetcher(api.get(`api/v1/activities/${id}`), ActivitySchema)
  },

  async create(data: CreateActivity): Promise<Activity> {
    const validated = CreateActivitySchema.parse(data)
    return fetcher(api.post('api/v1/activities', { json: validated }), ActivitySchema)
  },

  async update(id: string, data: UpdateActivity): Promise<Activity> {
    const validated = UpdateActivitySchema.parse(data)
    return fetcher(api.put(`api/v1/activities/${id}`, { json: validated }), ActivitySchema)
  },

  async delete(id: string): Promise<void> {
    await api.delete(`api/v1/activities/${id}`)
  },
}
