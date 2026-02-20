import { afterEach, describe, expect, it, vi } from 'vitest'
import { useToast } from '@/composables/useToast'
import type { ToastItem } from '@/types/toast'

type ToastPayload = Omit<ToastItem, 'id'>

describe('useToast', () => {
  afterEach(() => {
    const { setToastContainer } = useToast()
    setToastContainer(null)
    vi.restoreAllMocks()
  })

  it('showToast without container logs warning', () => {
    const warnSpy = vi.spyOn(console, 'warn').mockImplementation(() => undefined)
    const { showToast } = useToast()

    const result = showToast({ variant: 'success', title: 'Saved' })

    expect(result).toBeUndefined()
    expect(warnSpy).toHaveBeenCalledWith(
      'ToastContainer not found. Make sure it is mounted in App.vue',
    )
  })

  it('showToast with container calls addToast', () => {
    const addToast = vi.fn<(toast: ToastPayload) => string>().mockReturnValue('toast-1')
    const removeToast = vi.fn<(id: string) => void>()

    const { setToastContainer, showToast } = useToast()
    setToastContainer({ addToast, removeToast })

    const toast: ToastPayload = { variant: 'default', title: 'Hello', description: 'World' }
    const result = showToast(toast)

    expect(addToast).toHaveBeenCalledWith(toast)
    expect(result).toBe('toast-1')
  })

  it('success helper calls showToast with success variant', () => {
    const addToast = vi.fn<(toast: ToastPayload) => string>().mockReturnValue('toast-2')
    const removeToast = vi.fn<(id: string) => void>()

    const { setToastContainer, success } = useToast()
    setToastContainer({ addToast, removeToast })

    success('Done', 'Action completed', 2500)

    expect(addToast).toHaveBeenCalledWith({
      variant: 'success',
      title: 'Done',
      description: 'Action completed',
      duration: 2500,
    })
  })

  it('error helper calls showToast with error variant', () => {
    const addToast = vi.fn<(toast: ToastPayload) => string>().mockReturnValue('toast-3')
    const removeToast = vi.fn<(id: string) => void>()

    const { setToastContainer, error } = useToast()
    setToastContainer({ addToast, removeToast })

    error('Oops', 'Something failed', 3000)

    expect(addToast).toHaveBeenCalledWith({
      variant: 'error',
      title: 'Oops',
      description: 'Something failed',
      duration: 3000,
    })
  })

  it('warning helper calls showToast with warning variant', () => {
    const addToast = vi.fn<(toast: ToastPayload) => string>().mockReturnValue('toast-4')
    const removeToast = vi.fn<(id: string) => void>()

    const { setToastContainer, warning } = useToast()
    setToastContainer({ addToast, removeToast })

    warning('Careful', 'Check your input', 1500)

    expect(addToast).toHaveBeenCalledWith({
      variant: 'warning',
      title: 'Careful',
      description: 'Check your input',
      duration: 1500,
    })
  })

  it('info helper calls showToast with default variant', () => {
    const addToast = vi.fn<(toast: ToastPayload) => string>().mockReturnValue('toast-5')
    const removeToast = vi.fn<(id: string) => void>()

    const { setToastContainer, info } = useToast()
    setToastContainer({ addToast, removeToast })

    info('FYI', 'Heads up', 2000)

    expect(addToast).toHaveBeenCalledWith({
      variant: 'default',
      title: 'FYI',
      description: 'Heads up',
      duration: 2000,
    })
  })

  it('setToastContainer sets container ref', () => {
    const firstAddToast = vi.fn<(toast: ToastPayload) => string>().mockReturnValue('first')
    const secondAddToast = vi.fn<(toast: ToastPayload) => string>().mockReturnValue('second')
    const removeToast = vi.fn<(id: string) => void>()

    const { setToastContainer, showToast } = useToast()
    setToastContainer({ addToast: firstAddToast, removeToast })
    setToastContainer({ addToast: secondAddToast, removeToast })

    const result = showToast({ title: 'Latest container wins' })

    expect(firstAddToast).not.toHaveBeenCalled()
    expect(secondAddToast).toHaveBeenCalledWith({ title: 'Latest container wins' })
    expect(result).toBe('second')
  })
})
