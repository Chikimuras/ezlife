import { api, fetcher } from './client'
import { GlobalConstraintsSchema, type UpdateGlobalConstraints } from './schemas/globalConstraints'

export const globalConstraintsApi = {
  get: () => fetcher(api.get('api/v1/global-constraints'), GlobalConstraintsSchema),

  update: (data: UpdateGlobalConstraints) =>
    fetcher(api.patch('api/v1/global-constraints', { json: data }), GlobalConstraintsSchema),
}
