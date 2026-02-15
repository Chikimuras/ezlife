import { api, fetcher } from './client'
import { GroupSchema, type CreateGroup, type UpdateGroup } from './schemas/group'
import { z } from 'zod'

const GroupsListSchema = z.array(GroupSchema)

export const groupApi = {
  getAll: () => fetcher(api.get('api/v1/groups'), GroupsListSchema),

  getById: (id: string) => fetcher(api.get(`api/v1/groups/${id}`), GroupSchema),

  create: (data: CreateGroup) => fetcher(api.post('api/v1/groups', { json: data }), GroupSchema),

  update: (id: string, data: UpdateGroup) =>
    fetcher(api.patch(`api/v1/groups/${id}`, { json: data }), GroupSchema),

  delete: (id: string) => api.delete(`api/v1/groups/${id}`),
}
