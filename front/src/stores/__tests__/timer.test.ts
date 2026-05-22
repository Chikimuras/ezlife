import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useTimerStore } from '@/stores/timer'
import { timerApi } from '@/lib/api/timer'
import type { Activity } from '@/lib/api/schemas/activity'

const handleApiErrorMock = vi.fn(async () => undefined)
const routerPushMock = vi.fn()

vi.mock('@/lib/api/timer', () => ({
  timerApi: {
    start: vi.fn(),
    stop: vi.fn(),
    stopAt: vi.fn(),
    getActive: vi.fn(),
  },
}))

vi.mock('@/composables/useErrorHandler', () => ({
  useErrorHandler: () => ({
    handleAuthError: vi.fn(async () => undefined),
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

const runningActivity: Activity = {
  id: '11111111-1111-4111-8111-111111111111',
  date: '2026-02-21',
  startTime: '09:00',
  endTime: null,
  categoryId: 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',
  notes: undefined,
  createdAt: '2026-02-21T09:00:00.000Z',
  updatedAt: '2026-02-21T09:00:00.000Z',
  isFromTask: false,
}

const stoppedActivity: Activity = {
  ...runningActivity,
  endTime: '10:30',
}

describe('timer store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('startTimer success sets state correctly', async () => {
    const store = useTimerStore()
    vi.mocked(timerApi.start).mockResolvedValue(runningActivity)

    await store.startTimer(runningActivity.categoryId)

    expect(store.isRunning).toBe(true)
    expect(store.activeActivity).toEqual(runningActivity)
    expect(store.loading).toBe(false)
    expect(store.error).toBe(null)
  })

  it('startTimer failure sets error and calls handler', async () => {
    const store = useTimerStore()
    const failure = new Error('start failed')
    vi.mocked(timerApi.start).mockRejectedValue(failure)

    await expect(store.startTimer(runningActivity.categoryId)).rejects.toThrow('start failed')

    expect(store.error).toBe('Failed to start timer')
    expect(store.loading).toBe(false)
    expect(handleApiErrorMock).toHaveBeenCalledWith(failure, 'Starting Timer')
  })

  it('stopTimer success resets state', async () => {
    const store = useTimerStore()
    store.isRunning = true
    store.activeActivity = runningActivity
    store.currentElapsed = 5400
    vi.mocked(timerApi.stop).mockResolvedValue(stoppedActivity)

    await store.stopTimer()

    expect(store.isRunning).toBe(false)
    expect(store.activeActivity).toBe(null)
    expect(store.currentElapsed).toBe(0)
    expect(store.loading).toBe(false)
  })

  it('stopTimerAt success resets state', async () => {
    const store = useTimerStore()
    store.isRunning = true
    store.activeActivity = runningActivity
    store.currentElapsed = 5400
    vi.mocked(timerApi.stopAt).mockResolvedValue(stoppedActivity)

    await store.stopTimerAt('10:30')

    expect(timerApi.stopAt).toHaveBeenCalledWith('10:30')
    expect(store.isRunning).toBe(false)
    expect(store.activeActivity).toBe(null)
    expect(store.currentElapsed).toBe(0)
    expect(store.loading).toBe(false)
  })

  it('checkActiveTimer with active timer sets running state', async () => {
    const store = useTimerStore()
    vi.mocked(timerApi.getActive).mockResolvedValue(runningActivity)

    const result = await store.checkActiveTimer()

    expect(result).toEqual(runningActivity)
    expect(store.isRunning).toBe(true)
    expect(store.activeActivity).toEqual(runningActivity)
  })

  it('checkActiveTimer with no active timer keeps idle', async () => {
    const store = useTimerStore()
    vi.mocked(timerApi.getActive).mockResolvedValue(null)

    const result = await store.checkActiveTimer()

    expect(result).toBe(null)
    expect(store.isRunning).toBe(false)
    expect(store.activeActivity).toBe(null)
  })

  it('elapsedFormatted returns correct HH:mm:ss format', () => {
    const store = useTimerStore()
    store.currentElapsed = 3665

    expect(store.elapsedFormatted).toBe('01:01:05')
  })

  it('elapsedFormatted returns 00:00:00 when idle', () => {
    const store = useTimerStore()

    expect(store.elapsedFormatted).toBe('00:00:00')
  })

  it('clearTimer resets all state', () => {
    const store = useTimerStore()
    store.activeActivity = runningActivity
    store.isRunning = true
    store.loading = true
    store.error = 'Some timer error'
    store.currentElapsed = 42

    store.clearTimer()

    expect(store.activeActivity).toBe(null)
    expect(store.isRunning).toBe(false)
    expect(store.loading).toBe(false)
    expect(store.error).toBe(null)
    expect(store.currentElapsed).toBe(0)
  })

  it('loading toggles correctly around async action', async () => {
    const store = useTimerStore()
    let resolveRequest: ((value: Activity) => void) | undefined

    const pending = new Promise<Activity>((resolve) => {
      resolveRequest = resolve
    })

    vi.mocked(timerApi.start).mockReturnValue(pending)

    const request = store.startTimer(runningActivity.categoryId)
    expect(store.loading).toBe(true)

    resolveRequest?.(runningActivity)
    await request

    expect(store.loading).toBe(false)
  })
})

describe('timer flow scenarios', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('full flow: start then stop', async () => {
    const store = useTimerStore()
    vi.mocked(timerApi.start).mockResolvedValue(runningActivity)
    vi.mocked(timerApi.stop).mockResolvedValue(stoppedActivity)

    await store.startTimer('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa')
    expect(store.isRunning).toBe(true)
    expect(store.activeActivity).toEqual(runningActivity)

    await store.stopTimer()
    expect(store.isRunning).toBe(false)
    expect(store.activeActivity).toBeNull()
    expect(store.currentElapsed).toBe(0)
  })

  it('full flow: start then check on mount then continue', async () => {
    const store = useTimerStore()
    vi.mocked(timerApi.getActive).mockResolvedValue(runningActivity)

    const active = await store.checkActiveTimer()
    expect(active).toEqual(runningActivity)
    expect(store.isRunning).toBe(true)

    expect(store.isRunning).toBe(true)
  })

  it('full flow: check on mount then stop now', async () => {
    const store = useTimerStore()
    vi.mocked(timerApi.getActive).mockResolvedValue(runningActivity)
    vi.mocked(timerApi.stop).mockResolvedValue(stoppedActivity)

    await store.checkActiveTimer()
    expect(store.isRunning).toBe(true)

    await store.stopTimer()
    expect(store.isRunning).toBe(false)
    expect(store.activeActivity).toBeNull()
  })

  it('full flow: check on mount then stop at specific time', async () => {
    const store = useTimerStore()
    vi.mocked(timerApi.getActive).mockResolvedValue(runningActivity)
    vi.mocked(timerApi.stopAt).mockResolvedValue(stoppedActivity)

    await store.checkActiveTimer()
    expect(store.isRunning).toBe(true)

    await store.stopTimerAt('10:30')
    expect(store.isRunning).toBe(false)
    expect(timerApi.stopAt).toHaveBeenCalledWith('10:30')
  })
})

describe('edge cases', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('stopTimerAt calls API with correct time string', async () => {
    const store = useTimerStore()
    vi.mocked(timerApi.stopAt).mockResolvedValue(stoppedActivity)

    store.isRunning = true
    store.activeActivity = runningActivity

    await store.stopTimerAt('23:45')
    expect(timerApi.stopAt).toHaveBeenCalledWith('23:45')
    expect(store.isRunning).toBe(false)
  })

  it('elapsedFormatted handles hours correctly', () => {
    const store = useTimerStore()
    store.currentElapsed = 36000
    expect(store.elapsedFormatted).toBe('10:00:00')
  })
})
