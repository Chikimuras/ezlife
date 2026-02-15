import { api, fetcher } from './client'
import {
  DailyInsightSchema,
  WeeklyInsightSchema,
  type DailyInsight,
  type WeeklyInsight,
} from './schemas/insights'

export const insightsApi = {
  async getDailyComparison(date?: string): Promise<DailyInsight> {
    const url = date
      ? `api/v1/insights/daily-comparison?date=${date}`
      : 'api/v1/insights/daily-comparison'
    return fetcher(api.get(url), DailyInsightSchema)
  },

  async getWeeklyComparison(date?: string): Promise<WeeklyInsight> {
    const url = date
      ? `api/v1/insights/weekly-comparison?date=${date}`
      : 'api/v1/insights/weekly-comparison'
    return fetcher(api.get(url), WeeklyInsightSchema)
  },
}
