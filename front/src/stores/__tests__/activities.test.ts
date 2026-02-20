import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useActivitiesStore } from '@/stores/activities'
import { activityApi } from '@/lib/api/activity'
import type { Activity, CreateActivity, UpdateActivity } from '@/lib/api/schemas/activity'

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

const activityOne: Activity = {
  id: '11111111-1111-4111-8111-111111111111',
  date: '2024-01-01',
  startTime: '08:00',
  endTime: '09:00',
  categoryId: 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',
  notes: 'first',
  createdAt: '2024-01-01T00:00:00.000Z',
  updatedAt: '2024-01-01T00:00:00.000Z',
  isFromTask: false,
}

const activityTwo: Activity = {
  id: '22222222-2222-4222-8222-222222222222',
  date: '2024-01-02',
  startTime: '10:00',
  endTime: '11:00',
  categoryId: 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb',
  notes: 'second',
  createdAt: '2024-01-02T00:00:00.000Z',
  updatedAt: '2024-01-02T00:00:00.000Z',
  isFromTask: false,
}

describe('activities store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    vi.stubGlobal('localStorage', {
      getItem: vi.fn(() => null),
      setItem: vi.fn(),
      removeItem: vi.fn(),
    })
  })

  it('fetchActivities success updates activities list', async () => {
    const store = useActivitiesStore()
    vi.mocked(activityApi.getAll).mockResolvedValue([activityOne, activityTwo])

    await store.fetchActivities()

    expect(store.activities).toEqual([activityOne, activityTwo])
    expect(store.error).toBe(null)
    expect(store.loading).toBe(false)
  })

  it('fetchActivities failure sets error and calls handler', async () => {
    const store = useActivitiesStore()
    const failure = new Error('fetch failed')
    vi.mocked(activityApi.getAll).mockRejectedValue(failure)

    await expect(store.fetchActivities()).rejects.toThrow('fetch failed')

    expect(store.error).toBe('Failed to fetch activities')
    expect(store.loading).toBe(false)
    expect(handleApiErrorMock).toHaveBeenCalledWith(failure, 'Fetching Activities')
  })

  it('fetchActivitiesByDate success updates filtered list', async () => {
    const store = useActivitiesStore()
    vi.mocked(activityApi.getByDate).mockResolvedValue([activityOne])

    await store.fetchActivitiesByDate('2024-01-01')

    expect(activityApi.getByDate).toHaveBeenCalledWith('2024-01-01')
    expect(store.activities).toEqual([activityOne])
    expect(store.error).toBe(null)
  })

  it('createActivity success appends new item', async () => {
    const store = useActivitiesStore()
    const payload: CreateActivity = {
      date: '2024-01-03',
      startTime: '07:00',
      endTime: '08:00',
      categoryId: 'cccccccc-cccc-4ccc-8ccc-cccccccccccc',
      notes: 'new',
    }
    vi.mocked(activityApi.create).mockResolvedValue(activityTwo)

    const created = await store.createActivity(payload)

    expect(created).toEqual(activityTwo)
    expect(store.activities).toEqual([activityTwo])
  })

  it('updateActivity success replaces item in array', async () => {
    const store = useActivitiesStore()
    store.activities = [activityOne, activityTwo]

    const payload: UpdateActivity = { notes: 'updated notes' }
    const updated: Activity = { ...activityTwo, notes: 'updated notes' }
    vi.mocked(activityApi.update).mockResolvedValue(updated)

    const result = await store.updateActivity(activityTwo.id, payload)

    expect(result).toEqual(updated)
    expect(store.activities).toEqual([activityOne, updated])
  })

  it('deleteActivity success removes matching item', async () => {
    const store = useActivitiesStore()
    store.activities = [activityOne, activityTwo]
    vi.mocked(activityApi.delete).mockResolvedValue(undefined)

    await store.deleteActivity(activityOne.id)

    expect(activityApi.delete).toHaveBeenCalledWith(activityOne.id)
    expect(store.activities).toEqual([activityTwo])
  })

  it('loading toggles correctly around async action', async () => {
    const store = useActivitiesStore()
    let resolveRequest: ((value: Activity[]) => void) | undefined

    const pending = new Promise<Activity[]>((resolve) => {
      resolveRequest = resolve
    })

    vi.mocked(activityApi.getAll).mockReturnValue(pending)

    const request = store.fetchActivities()
    expect(store.loading).toBe(true)

    resolveRequest?.([activityOne])
    await request

    expect(store.loading).toBe(false)
  })
})
