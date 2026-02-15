export interface ToastItem {
  id: string
  variant?: 'default' | 'success' | 'error' | 'warning'
  title?: string
  description?: string
  duration?: number
}
