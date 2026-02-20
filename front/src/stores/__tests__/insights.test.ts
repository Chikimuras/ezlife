import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useInsightsStore } from '@/stores/insights'
import { insightsApi } from '@/lib/api/insights'
import type { DailyInsight, WeeklyInsight } from '@/lib/api/schemas/insights'

const handleAuthErrorMock = vi.fn(async () => undefined)
const handleApiErrorMock = vi.fn(async () => undefined)
const routerPushMock = vi.fn()

vi.mock('@/lib/api/auth', () => ({
  authApi: {
    loginWithGoogle: vi.fn(),
    me: vi.fn(),
    refresh: vi.fn(),
    logout: vi.fn(),
  },
}))

vi.mock('@/lib/api/activity', () => ({
  activityApi: {
    getAll: vi.fn(),
    getByDate: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
  },
}))

vi.mock('@/lib/api/insights', () => ({
  insightsApi: {
    getDailyComparison: vi.fn(),
    getWeeklyComparison: vi.fn(),
  },
}))

vi.mock('@/composables/useErrorHandler', () => ({
  useErrorHandler: () => ({
    handleAuthError: handleAuthErrorMock,
    handleApiError: handleApiErrorMock,
  }),
}))

vi.mock('@/lib/errors/errorLogger', () => ({
  errorLogger: {
    logInfo: vi.fn(),
    logError: vi.fn(),
    logWarning: vi.fn(),
  },
}))

vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string) => key,
  }),
}))

vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: routerPushMock,
  }),
}))

const dailyInsight: DailyInsight = {
  date: '2024-01-05',
  previousDate: '2024-01-04',
  totalMinutes: 300,
  previousTotalMinutes: 240,
  totalMinutesDelta: 60,
  totalMinutesPercentChange: 25,
  groupBreakdown: [],
  topCategories: [],
  stats: {
    activitiesCount: 4,
    previousActivitiesCount: 3,
    activitiesCountDelta: 1,
    categoriesUsed: 2,
    previousCategoriesUsed: 2,
    categoriesUsedDelta: 0,
    averageActivityDuration: 75,
    previousAverageActivityDuration: 80,
    averageActivityDurationDelta: -5,
    longestActivity: null,
    shortestActivity: null,
  },
  productivity: {
    mandatoryMinutes: 120,
    previousMandatoryMinutes: 90,
    mandatoryMinutesDelta: 30,
    mandatoryPercentOfTotal: 40,
  },
}

const weeklyInsight: WeeklyInsight = {
  weekStartDate: '2024-01-01',
  weekEndDate: '2024-01-07',
  previousWeekStartDate: '2023-12-25',
  previousWeekEndDate: '2023-12-31',
  totalMinutes: 1800,
  previousTotalMinutes: 1500,
  totalMinutesDelta: 300,
  totalMinutesPercentChange: 20,
  groupBreakdown: [],
  topCategories: [],
  stats: {
    activitiesCount: 20,
    previousActivitiesCount: 16,
    activitiesCountDelta: 4,
    categoriesUsed: 5,
    previousCategoriesUsed: 4,
    categoriesUsedDelta: 1,
    averageActivityDuration: 90,
    previousAverageActivityDuration: 94,
    averageActivityDurationDelta: -4,
    averageDailyMinutes: 257,
    previousAverageDailyMinutes: 214,
    averageDailyMinutesDelta: 43,
    mostProductiveDay: null,
    leastProductiveDay: null,
    longestActivity: null,
  },
  dailyBreakdown: [],
  goalsProgress: null,
}

describe('insights store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    vi.stubGlobal('localStorage', {
      getItem: vi.fn(() => null),
      setItem: vi.fn(),
      removeItem: vi.fn(),
    })
  })

  it('fetchDailyComparison success stores daily insight', async () => {
    const store = useInsightsStore()
    vi.mocked(insightsApi.getDailyComparison).mockResolvedValue(dailyInsight)

    await store.fetchDailyComparison('2024-01-05')

    expect(insightsApi.getDailyComparison).toHaveBeenCalledWith('2024-01-05')
    expect(store.dailyInsight).toEqual(dailyInsight)
    expect(store.error).toBe(null)
  })

  it('fetchDailyComparison failure sets error and calls handler', async () => {
    const store = useInsightsStore()
    const failure = new Error('daily failed')
    vi.mocked(insightsApi.getDailyComparison).mockRejectedValue(failure)

    await expect(store.fetchDailyComparison()).rejects.toThrow('daily failed')

    expect(store.error).toBe('Failed to fetch daily insights')
    expect(handleApiErrorMock).toHaveBeenCalledWith(failure, 'Fetching Daily Insights')
    expect(store.loading).toBe(false)
  })

  it('fetchWeeklyComparison success stores weekly insight', async () => {
    const store = useInsightsStore()
    vi.mocked(insightsApi.getWeeklyComparison).mockResolvedValue(weeklyInsight)

    await store.fetchWeeklyComparison('2024-01-05')

    expect(insightsApi.getWeeklyComparison).toHaveBeenCalledWith('2024-01-05')
    expect(store.weeklyInsight).toEqual(weeklyInsight)
    expect(store.error).toBe(null)
  })

  it('fetchWeeklyComparison failure sets error and calls handler', async () => {
    const store = useInsightsStore()
    const failure = new Error('weekly failed')
    vi.mocked(insightsApi.getWeeklyComparison).mockRejectedValue(failure)

    await expect(store.fetchWeeklyComparison()).rejects.toThrow('weekly failed')

    expect(store.error).toBe('Failed to fetch weekly insights')
    expect(handleApiErrorMock).toHaveBeenCalledWith(failure, 'Fetching Weekly Insights')
    expect(store.loading).toBe(false)
  })

  it('loading toggles correctly around insights requests', async () => {
    const store = useInsightsStore()
    let resolveRequest: ((value: DailyInsight) => void) | undefined
    const pending = new Promise<DailyInsight>((resolve) => {
      resolveRequest = resolve
    })

    vi.mocked(insightsApi.getDailyComparison).mockReturnValue(pending)

    const request = store.fetchDailyComparison('2024-01-05')
    expect(store.loading).toBe(true)

    resolveRequest?.(dailyInsight)
    await request

    expect(store.loading).toBe(false)
  })
})
