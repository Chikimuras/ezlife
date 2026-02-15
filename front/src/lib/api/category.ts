import { api, fetcher } from './client'
import { CategorySchema, type CreateCategory, type UpdateCategory } from './schemas/category'
import { z } from 'zod'

const CategoriesListSchema = z.array(CategorySchema)

export const categoryApi = {
  getAll: () => fetcher(api.get('api/v1/categories'), CategoriesListSchema),

  getById: (id: string) => fetcher(api.get(`api/v1/categories/${id}`), CategorySchema),

  create: (data: CreateCategory) =>
    fetcher(api.post('api/v1/categories', { json: data }), CategorySchema),

  update: (id: string, data: UpdateCategory) =>
    fetcher(api.patch(`api/v1/categories/${id}`, { json: data }), CategorySchema),

  delete: (id: string) => api.delete(`api/v1/categories/${id}`),
}
