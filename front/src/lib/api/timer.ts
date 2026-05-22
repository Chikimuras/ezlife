import { HTTPError } from 'ky'
import { api, fetcher } from './client'
import { ActivitySchema, type Activity } from './schemas/activity'

export const timerApi = {
  async start(categoryId: string): Promise<Activity> {
    return fetcher(api.post('api/v1/timer/start', { json: { categoryId } }), ActivitySchema)
  },

  async stop(): Promise<Activity> {
    return fetcher(api.post('api/v1/timer/stop'), ActivitySchema)
  },

  async stopAt(endTime: string): Promise<Activity> {
    return fetcher(api.post('api/v1/timer/stop-at', { json: { endTime } }), ActivitySchema)
  },

  async getActive(): Promise<Activity | null> {
    try {
      return await fetcher(api.get('api/v1/timer/active'), ActivitySchema)
    } catch (error) {
      if (error instanceof HTTPError && error.response.status === 404) {
        return null
      }
      throw error
    }
  },
}
