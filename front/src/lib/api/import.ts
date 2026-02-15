import { api } from './client'

export interface ImportResponse {
  groupsCreated: number
  categoriesCreated: number
  activitiesCreated: number
  errors: string[]
}

export const importApi = {
  async uploadExcel(file: File): Promise<ImportResponse> {
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post('api/v1/import/excel', {
      body: formData,
    })

    return response.json<ImportResponse>()
  },
}
