<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import AuthenticatedLayout from '@/components/layouts/AuthenticatedLayout.vue'
import Button from '@/components/ui/Button.vue'
import ActivityDialog from '@/components/features/ActivityDialog.vue'
import { useActivitiesStore } from '@/stores/activities'
import { useCategoriesStore } from '@/stores/categories'
import { useGroupsStore } from '@/stores/groups'
import { useTimerStore } from '@/stores/timer'
import { useToast } from '@/composables/useToast'
import type { CreateActivity, Activity, UpdateActivity } from '@/lib/api/schemas/activity'
import ActivityTimer from '@/components/features/ActivityTimer.vue'
import CategorySelector from '@/components/features/CategorySelector.vue'
import ActiveTimerDialog from '@/components/features/ActiveTimerDialog.vue'

const { t } = useI18n()
const { success, error } = useToast()
const activitiesStore = useActivitiesStore()
const categoriesStore = useCategoriesStore()
const groupsStore = useGroupsStore()
const timerStore = useTimerStore()
const isCategorySelectorOpen = ref(false)
const isActiveTimerDialogOpen = ref(false)

const activeTimerCategoryName = computed(() => {
  if (!timerStore.activeActivity) return ''
  return (
    categoriesStore.categories.find((c) => c.id === timerStore.activeActivity?.categoryId)?.name ??
    t('activities.timer.categoryUnavailable')
  )
})

// Restore view mode from localStorage or default to 'day'
const savedViewMode = localStorage.getItem('activities-view-mode') as 'day' | 'week' | null
const viewMode = ref<'day' | 'week'>(savedViewMode ?? 'day')
const selectedDate = ref(new Date())
const formattedDate = computed(() => {
  const isoString = selectedDate.value.toISOString().split('T')[0]
  return isoString ?? ''
})

const isActivityDialogOpen = ref(false)
const clickedTimeSlot = ref('')
const editingActivityId = ref<string | null>(null)

const draggedActivity = ref<string | null>(null)
const dragStartY = ref(0)
const dragStartX = ref(0)
const dragStartTop = ref(0)
const isDragging = ref(false)
const mouseDownTime = ref(0)
const hasMoved = ref(false)
const resizeMode = ref<'none' | 'top' | 'bottom'>('none')
const resizeStartHeight = ref(0)
const dragStartDate = ref<string | null>(null)
const hoveredActivity = ref<string | null>(null)
const tooltipPosition = ref({ x: 0, y: 0 })

const timeSlots = Array.from({ length: 24 }, (_, i) => {
  const hour = i.toString().padStart(2, '0')
  return `${hour}:00`
})

onMounted(async () => {
  await Promise.all([categoriesStore.fetchCategories(), groupsStore.fetchGroups()])

  if (viewMode.value === 'week') {
    await fetchWeekActivities()
  } else {
    await activitiesStore.fetchActivitiesByDate(formattedDate.value)
  }

  const activeTimer = await timerStore.checkActiveTimer()
  if (activeTimer) {
    isActiveTimerDialogOpen.value = true
  }
})

const goToPreviousDay = () => {
  const newDate = new Date(selectedDate.value)
  newDate.setDate(newDate.getDate() - 1)
  selectedDate.value = newDate
  activitiesStore.fetchActivitiesByDate(formattedDate.value)
}

const goToNextDay = () => {
  const newDate = new Date(selectedDate.value)
  newDate.setDate(newDate.getDate() + 1)
  selectedDate.value = newDate
  activitiesStore.fetchActivitiesByDate(formattedDate.value)
}

const goToToday = () => {
  selectedDate.value = new Date()
  if (viewMode.value === 'day') {
    activitiesStore.fetchActivitiesByDate(formattedDate.value)
  } else {
    fetchWeekActivities()
  }
}

const goToPreviousWeek = () => {
  const newDate = new Date(selectedDate.value)
  newDate.setDate(newDate.getDate() - 7)
  selectedDate.value = newDate
  fetchWeekActivities()
}

const goToNextWeek = () => {
  const newDate = new Date(selectedDate.value)
  newDate.setDate(newDate.getDate() + 7)
  selectedDate.value = newDate
  fetchWeekActivities()
}

const getWeekDates = computed(() => {
  const current = new Date(selectedDate.value)
  const dayOfWeek = current.getDay()
  const diff = dayOfWeek === 0 ? -6 : 1 - dayOfWeek // Monday = start of week
  const monday = new Date(current)
  monday.setDate(current.getDate() + diff)

  return Array.from({ length: 7 }, (_, i) => {
    const date = new Date(monday)
    date.setDate(monday.getDate() + i)
    return date
  })
})

const getActivitiesForDate = (date: Date) => {
  const dateStr = date.toISOString().split('T')[0] ?? ''
  return activitiesStore.activities.filter((activity) => activity.date === dateStr)
}

const getWeekLabel = computed(() => {
  const dates = getWeekDates.value
  const firstDay = dates[0]
  const lastDay = dates[6]

  if (!firstDay || !lastDay) return ''

  const formatter = new Intl.DateTimeFormat('fr-FR', {
    day: 'numeric',
    month: 'short',
  })

  return `${formatter.format(firstDay)} - ${formatter.format(lastDay)}`
})

const fetchWeekActivities = async () => {
  const dates = getWeekDates.value.map((date) => date.toISOString().split('T')[0] ?? '')
  await activitiesStore.fetchActivitiesByDateRange(dates)
}

const switchViewMode = (mode: 'day' | 'week') => {
  viewMode.value = mode
  localStorage.setItem('activities-view-mode', mode)
  if (mode === 'week') {
    fetchWeekActivities()
  } else {
    activitiesStore.fetchActivitiesByDate(formattedDate.value)
  }
}

const getDateLabel = computed(() => {
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)
  const tomorrow = new Date(today)
  tomorrow.setDate(tomorrow.getDate() + 1)

  const selectedDateStr = formattedDate.value
  const todayStr = today.toISOString().split('T')[0]
  const yesterdayStr = yesterday.toISOString().split('T')[0]
  const tomorrowStr = tomorrow.toISOString().split('T')[0]

  if (selectedDateStr === todayStr) return t('activities.today')
  if (selectedDateStr === yesterdayStr) return t('activities.yesterday')
  if (selectedDateStr === tomorrowStr) return t('activities.tomorrow')

  return selectedDate.value.toLocaleDateString('fr-FR', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
})

const handleTimeSlotClick = (timeSlot: string) => {
  clickedTimeSlot.value = timeSlot
  editingActivityId.value = null
  isActivityDialogOpen.value = true
}

const handleWeekTimeSlotClick = (date: Date, timeSlot: string) => {
  selectedDate.value = date
  handleTimeSlotClick(timeSlot)
}

const handleActivityClick = (activity: Activity) => {
  if (hasMoved.value) {
    hasMoved.value = false
    return
  }
  editingActivityId.value = activity.id
  clickedTimeSlot.value = activity.startTime
  isActivityDialogOpen.value = true
}

const handleSaveActivity = async (data: CreateActivity) => {
  try {
    if (editingActivityId.value) {
      await activitiesStore.updateActivity(editingActivityId.value, data as UpdateActivity)
      success(t('activities.messages.updated'))
    } else {
      await activitiesStore.createActivity(data)
      success(t('activities.messages.created'))
    }
    editingActivityId.value = null
  } catch {
    error(
      editingActivityId.value
        ? t('activities.messages.updateError')
        : t('activities.messages.createError'),
    )
  }
}

const handleDeleteActivity = async (activityId: string) => {
  try {
    await activitiesStore.deleteActivity(activityId)
    success(t('activities.messages.deleted'))
    isActivityDialogOpen.value = false
    editingActivityId.value = null
  } catch {
    error(t('activities.messages.deleteError'))
  }
}

const handleDragStart = (activity: Activity, event: MouseEvent) => {
  event.preventDefault()
  draggedActivity.value = activity.id
  dragStartY.value = event.clientY
  dragStartX.value = event.clientX
  dragStartTop.value = parseInt(getActivityStyle(activity).top)
  dragStartDate.value = activity.date
  mouseDownTime.value = Date.now()
  hasMoved.value = false
  resizeMode.value = 'none'

  const handleMouseMove = (e: MouseEvent) => {
    if (!draggedActivity.value) return

    const deltaY = Math.abs(e.clientY - dragStartY.value)
    const deltaX = Math.abs(e.clientX - dragStartX.value)
    const timeSinceMouseDown = Date.now() - mouseDownTime.value

    if (deltaY > 5 || deltaX > 5 || timeSinceMouseDown > 200) {
      hasMoved.value = true
      isDragging.value = true
    }

    if (!hasMoved.value) return

    const actualDeltaY = e.clientY - dragStartY.value
    const newTopRaw = Math.max(0, Math.min(1440 - 30, dragStartTop.value + actualDeltaY))

    const newTopSnapped = snapToInterval(newTopRaw, 15)

    const activityElement = document.querySelector(`[data-activity-id="${draggedActivity.value}"]`)
    if (activityElement instanceof HTMLElement) {
      activityElement.style.top = `${newTopSnapped}px`

      // In week view, handle horizontal movement for day change
      if (viewMode.value === 'week') {
        const actualDeltaX = e.clientX - dragStartX.value

        // Get the week grid container to calculate column width
        const weekGrid = document.querySelector(
          '.grid.grid-cols-\\[80px_repeat\\(7\\,minmax\\(120px\\,1fr\\)\\)\\]',
        )
        if (weekGrid) {
          const gridRect = weekGrid.getBoundingClientRect()
          const columnWidth = (gridRect.width - 80) / 7 // Subtract time column width, divide by 7 days
          const dayShift = Math.round(actualDeltaX / columnWidth)

          // Visual feedback: show which day column we're over
          if (dayShift !== 0) {
            activityElement.style.opacity = '0.6'
          } else {
            activityElement.style.opacity = '1'
          }
        }
      }
    }
  }

  const handleMouseUp = () => {
    if (!draggedActivity.value) return

    if (!hasMoved.value) {
      draggedActivity.value = null
      isDragging.value = false
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
      return
    }

    const activity = activitiesStore.activities.find((a) => a.id === draggedActivity.value)
    if (!activity) {
      draggedActivity.value = null
      isDragging.value = false
      hasMoved.value = false
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
      return
    }

    if (!activity.endTime) {
      // Cannot drag a running timer activity
      draggedActivity.value = null
      isDragging.value = false
      hasMoved.value = false
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
      return
    }

    const activityElement = document.querySelector(`[data-activity-id="${draggedActivity.value}"]`)
    if (!(activityElement instanceof HTMLElement)) {
      draggedActivity.value = null
      isDragging.value = false
      hasMoved.value = false
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
      return
    }

    // Reset opacity
    activityElement.style.opacity = '1'

    const newTop = parseInt(activityElement.style.top)
    const newStartMinutes = Math.round(newTop / 1)
    const newStartHours = Math.floor(newStartMinutes / 60)
    const newStartMins = newStartMinutes % 60

    const oldStartParts = activity.startTime.split(':')
    const oldEndParts = activity.endTime.split(':')
    const oldStartMinutes =
      parseInt(oldStartParts[0] ?? '0') * 60 + parseInt(oldStartParts[1] ?? '0')
    const oldEndMinutes = parseInt(oldEndParts[0] ?? '0') * 60 + parseInt(oldEndParts[1] ?? '0')
    const durationMinutes = oldEndMinutes - oldStartMinutes

    const newEndMinutes = newStartMinutes + durationMinutes
    const newEndHours = Math.floor(newEndMinutes / 60)
    const newEndMins = newEndMinutes % 60

    const newStartTime = `${newStartHours.toString().padStart(2, '0')}:${newStartMins.toString().padStart(2, '0')}`
    const newEndTime = `${newEndHours.toString().padStart(2, '0')}:${newEndMins.toString().padStart(2, '0')}`

    // Calculate new date if in week view
    let newDate = activity.date
    if (viewMode.value === 'week' && dragStartDate.value) {
      const actualDeltaX = event.clientX - dragStartX.value
      const weekGrid = document.querySelector(
        '.grid.grid-cols-\\[80px_repeat\\(7\\,minmax\\(120px\\,1fr\\)\\)\\]',
      )

      if (weekGrid) {
        const gridRect = weekGrid.getBoundingClientRect()
        const columnWidth = (gridRect.width - 80) / 7
        const dayShift = Math.round(actualDeltaX / columnWidth)

        if (dayShift !== 0) {
          const originalDate = new Date(dragStartDate.value)
          originalDate.setDate(originalDate.getDate() + dayShift)
          newDate = originalDate.toISOString().split('T')[0] ?? activity.date
        }
      }
    }

    if (hasTimeConflict(activity.id, newStartTime, newEndTime, newDate)) {
      activityElement.style.top = `${dragStartTop.value}px`
      error(t('activities.messages.conflictError'))
    } else {
      const updateData: UpdateActivity = {
        startTime: newStartTime,
        endTime: newEndTime,
      }

      // Only include date if it changed
      if (newDate !== activity.date) {
        updateData.date = newDate
      }

      activitiesStore
        .updateActivity(activity.id, updateData)
        .then(() => {
          success(t('activities.messages.updated'))
          // Refresh activities if date changed
          if (newDate !== activity.date && viewMode.value === 'week') {
            fetchWeekActivities()
          }
        })
        .catch(() => {
          activityElement.style.top = `${dragStartTop.value}px`
          error(t('activities.messages.updateError'))
        })
    }

    draggedActivity.value = null
    dragStartDate.value = null
    setTimeout(() => {
      isDragging.value = false
      hasMoved.value = false
    }, 100)
    document.removeEventListener('mousemove', handleMouseMove)
    document.removeEventListener('mouseup', handleMouseUp)
  }

  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

const handleResizeStart = (activity: Activity, mode: 'top' | 'bottom', event: MouseEvent) => {
  event.preventDefault()
  event.stopPropagation()

  draggedActivity.value = activity.id
  dragStartY.value = event.clientY
  dragStartTop.value = parseInt(getActivityStyle(activity).top)
  resizeStartHeight.value = parseInt(getActivityStyle(activity).height)
  mouseDownTime.value = Date.now()
  hasMoved.value = false
  resizeMode.value = mode

  const handleMouseMove = (e: MouseEvent) => {
    if (!draggedActivity.value || resizeMode.value === 'none') return

    const deltaY = Math.abs(e.clientY - dragStartY.value)
    const timeSinceMouseDown = Date.now() - mouseDownTime.value

    if (deltaY > 5 || timeSinceMouseDown > 200) {
      hasMoved.value = true
      isDragging.value = true
    }

    if (!hasMoved.value) return

    const actualDeltaY = e.clientY - dragStartY.value
    const activityElement = document.querySelector(`[data-activity-id="${draggedActivity.value}"]`)
    if (!(activityElement instanceof HTMLElement)) return

    if (resizeMode.value === 'top') {
      // Resize from top: change top position and height
      let newTopRaw = Math.max(0, dragStartTop.value + actualDeltaY)
      const maxTop = dragStartTop.value + resizeStartHeight.value - 15 // Min 15 min duration
      newTopRaw = Math.min(newTopRaw, maxTop)

      const newTopSnapped = snapToInterval(newTopRaw, 15)
      const newHeight = dragStartTop.value + resizeStartHeight.value - newTopSnapped

      activityElement.style.top = `${newTopSnapped}px`
      activityElement.style.height = `${newHeight}px`
    } else if (resizeMode.value === 'bottom') {
      // Resize from bottom: change height only
      let newHeightRaw = Math.max(15, resizeStartHeight.value + actualDeltaY) // Min 15 min
      const maxHeight = 1440 - dragStartTop.value
      newHeightRaw = Math.min(newHeightRaw, maxHeight)

      const newHeightSnapped = snapToInterval(newHeightRaw, 15)
      activityElement.style.height = `${newHeightSnapped}px`
    }
  }

  const handleMouseUp = () => {
    if (!draggedActivity.value || resizeMode.value === 'none') return

    if (!hasMoved.value) {
      draggedActivity.value = null
      isDragging.value = false
      resizeMode.value = 'none'
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
      return
    }

    const activity = activitiesStore.activities.find((a) => a.id === draggedActivity.value)
    if (!activity) {
      draggedActivity.value = null
      isDragging.value = false
      hasMoved.value = false
      resizeMode.value = 'none'
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
      return
    }

    if (!activity.endTime) {
      // Cannot resize a running timer activity
      draggedActivity.value = null
      isDragging.value = false
      hasMoved.value = false
      resizeMode.value = 'none'
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
      return
    }

    const activityElement = document.querySelector(`[data-activity-id="${draggedActivity.value}"]`)
    if (!(activityElement instanceof HTMLElement)) {
      draggedActivity.value = null
      isDragging.value = false
      hasMoved.value = false
      resizeMode.value = 'none'
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
      return
    }

    const newTop = parseInt(activityElement.style.top)
    const newHeight = parseInt(activityElement.style.height)

    const newStartMinutes = Math.round(newTop / 1)
    const newEndMinutes = Math.round((newTop + newHeight) / 1)

    const newStartHours = Math.floor(newStartMinutes / 60)
    const newStartMins = newStartMinutes % 60
    const newEndHours = Math.floor(newEndMinutes / 60)
    const newEndMins = newEndMinutes % 60

    const newStartTime = `${newStartHours.toString().padStart(2, '0')}:${newStartMins.toString().padStart(2, '0')}`
    const newEndTime = `${newEndHours.toString().padStart(2, '0')}:${newEndMins.toString().padStart(2, '0')}`

    if (hasTimeConflict(activity.id, newStartTime, newEndTime, activity.date)) {
      activityElement.style.top = `${dragStartTop.value}px`
      activityElement.style.height = `${resizeStartHeight.value}px`
      error(t('activities.messages.conflictError'))
    } else {
      activitiesStore
        .updateActivity(activity.id, {
          startTime: newStartTime,
          endTime: newEndTime,
        })
        .then(() => {
          success(t('activities.messages.updated'))
        })
        .catch(() => {
          activityElement.style.top = `${dragStartTop.value}px`
          activityElement.style.height = `${resizeStartHeight.value}px`
          error(t('activities.messages.updateError'))
        })
    }

    draggedActivity.value = null
    setTimeout(() => {
      isDragging.value = false
      hasMoved.value = false
      resizeMode.value = 'none'
    }, 100)
    document.removeEventListener('mousemove', handleMouseMove)
    document.removeEventListener('mouseup', handleMouseUp)
  }

  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

const hasTimeConflict = (
  activityId: string,
  startTime: string,
  endTime: string,
  date?: string,
): boolean => {
  const startParts = startTime.split(':')
  const endParts = endTime.split(':')
  const startMinutes = parseInt(startParts[0] ?? '0') * 60 + parseInt(startParts[1] ?? '0')
  const endMinutes = parseInt(endParts[0] ?? '0') * 60 + parseInt(endParts[1] ?? '0')

  return activitiesStore.activities.some((activity) => {
    if (activity.id === activityId) return false

    // If date is provided, only check conflicts on that date
    if (date && activity.date !== date) return false

    if (!activity.endTime) return false

    const actStartParts = activity.startTime.split(':')
    const actEndParts = activity.endTime.split(':')
    const actStartMinutes =
      parseInt(actStartParts[0] ?? '0') * 60 + parseInt(actStartParts[1] ?? '0')
    const actEndMinutes = parseInt(actEndParts[0] ?? '0') * 60 + parseInt(actEndParts[1] ?? '0')

    return (
      (startMinutes >= actStartMinutes && startMinutes < actEndMinutes) ||
      (endMinutes > actStartMinutes && endMinutes <= actEndMinutes) ||
      (startMinutes <= actStartMinutes && endMinutes >= actEndMinutes)
    )
  })
}

const getEditingActivity = computed(() => {
  if (!editingActivityId.value) return null
  return activitiesStore.activities.find((a) => a.id === editingActivityId.value) ?? null
})

const getCategoryColor = (categoryId: string): string => {
  const category = categoriesStore.categories.find((c) => c.id === categoryId)
  if (!category) return '#d1d5db'
  const group = groupsStore.groups.find((g) => g.id === category.groupId)
  return group?.color ?? '#d1d5db'
}

const getActivityStyle = (activity: (typeof activitiesStore.activities)[0]) => {
  const startParts = activity.startTime.split(':')

  if (!activity.endTime) {
    const startMinutes = parseInt(startParts[0] ?? '0') * 60 + parseInt(startParts[1] ?? '0')
    const now = new Date()
    const nowMinutes = now.getHours() * 60 + now.getMinutes()
    const durationMinutes = Math.max(30, nowMinutes - startMinutes)
    const top = startMinutes
    return {
      top: `${top}px`,
      height: `${durationMinutes}px`,
      backgroundColor: getCategoryColor(activity.categoryId),
    }
  }

  const endParts = activity.endTime.split(':')

  const startMinutes = parseInt(startParts[0] ?? '0') * 60 + parseInt(startParts[1] ?? '0')
  const endMinutes = parseInt(endParts[0] ?? '0') * 60 + parseInt(endParts[1] ?? '0')
  const durationMinutes = endMinutes - startMinutes

  const startHour = parseInt(startParts[0] ?? '0')
  const startMinute = parseInt(startParts[1] ?? '0')

  const top = (startHour * 60 + startMinute) * 1
  const height = durationMinutes * 1

  return {
    top: `${top}px`,
    height: `${height}px`,
    backgroundColor:
      activity.isFromTask && activity.taskListColor
        ? activity.taskListColor
        : getCategoryColor(activity.categoryId),
  }
}

const getCategoryName = (categoryId: string): string => {
  return categoriesStore.categories.find((c) => c.id === categoryId)?.name ?? ''
}

const getActivityDisplayName = (activity: Activity): string => {
  if (activity.isFromTask && activity.taskName) {
    return activity.taskName
  }
  return getCategoryName(activity.categoryId)
}

const snapToInterval = (minutes: number, snapInterval: number = 15): number => {
  const remainder = minutes % snapInterval
  if (remainder < snapInterval / 2) {
    return minutes - remainder
  } else {
    return minutes + (snapInterval - remainder)
  }
}

const getActivityDuration = (activity: Activity): string => {
  if (!activity.endTime) return t('activities.timer.running')

  const startParts = activity.startTime.split(':')
  const endParts = activity.endTime.split(':')
  const startMinutes = parseInt(startParts[0] ?? '0') * 60 + parseInt(startParts[1] ?? '0')
  const endMinutes = parseInt(endParts[0] ?? '0') * 60 + parseInt(endParts[1] ?? '0')
  const durationMinutes = endMinutes - startMinutes

  if (durationMinutes < 60) {
    return `${durationMinutes}min`
  } else {
    const hours = Math.floor(durationMinutes / 60)
    const mins = durationMinutes % 60
    return mins > 0 ? `${hours}h ${mins}min` : `${hours}h`
  }
}

const shouldShowText = (activity: Activity): boolean => {
  if (!activity.endTime) return true

  const startParts = activity.startTime.split(':')
  const endParts = activity.endTime.split(':')
  const startMinutes = parseInt(startParts[0] ?? '0') * 60 + parseInt(startParts[1] ?? '0')
  const endMinutes = parseInt(endParts[0] ?? '0') * 60 + parseInt(endParts[1] ?? '0')
  const durationMinutes = endMinutes - startMinutes
  return durationMinutes >= 30
}

const quarterHourMarkers = Array.from({ length: 24 * 4 }, (_, i) => i * 15)

const handleActivityMouseEnter = (activity: Activity, event: MouseEvent) => {
  hoveredActivity.value = activity.id
  const rect = (event.currentTarget as HTMLElement).getBoundingClientRect()
  tooltipPosition.value = {
    x: rect.right + 8,
    y: rect.top + rect.height / 2,
  }
}

const handleActivityMouseLeave = () => {
  hoveredActivity.value = null
}

const getHoveredActivity = computed(() => {
  if (!hoveredActivity.value) return null
  return activitiesStore.activities.find((a) => a.id === hoveredActivity.value) ?? null
})
const handleStartTimerClick = () => {
  isCategorySelectorOpen.value = true
}

const handleCategorySelected = async (categoryId: string) => {
  try {
    await timerStore.startTimer(categoryId)
    success(t('activities.messages.created'))
  } catch {
    error(t('activities.messages.createError'))
  }
}

const handleTimerStop = async () => {
  try {
    await timerStore.stopTimer()
    success(t('activities.messages.updated'))
    await activitiesStore.fetchActivitiesByDate(formattedDate.value)
  } catch {
    error(t('activities.messages.updateError'))
  }
}

const handleTimerContinue = () => {
  isActiveTimerDialogOpen.value = false
}

const handleTimerStopNow = async () => {
  try {
    await timerStore.stopTimer()
    success(t('activities.messages.updated'))
    await activitiesStore.fetchActivitiesByDate(formattedDate.value)
  } catch {
    error(t('activities.messages.updateError'))
  }
}

const handleTimerStopAt = async (endTime: string) => {
  try {
    await timerStore.stopTimerAt(endTime)
    success(t('activities.messages.updated'))
    await activitiesStore.fetchActivitiesByDate(formattedDate.value)
  } catch {
    error(t('activities.messages.updateError'))
  }
}
</script>

<template>
  <AuthenticatedLayout>
    <div class="h-full flex flex-col">
      <div class="bg-white border-b border-gray-200 px-4 py-4">
        <div class="flex items-center justify-between mb-4">
          <h1 class="text-xl font-semibold">{{ t('activities.title') }}</h1>
          <div class="flex items-center space-x-2">
            <!-- View Mode Toggle -->
            <div class="inline-flex rounded-lg border border-gray-200 p-1">
              <button
                :class="[
                  'px-3 py-1.5 text-sm font-medium rounded-md transition-colors',
                  viewMode === 'day'
                    ? 'bg-primary-500 text-white'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50',
                ]"
                @click="switchViewMode('day')"
              >
                {{ t('activities.viewMode.day') }}
              </button>
              <button
                :class="[
                  'px-3 py-1.5 text-sm font-medium rounded-md transition-colors',
                  viewMode === 'week'
                    ? 'bg-primary-500 text-white'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50',
                ]"
                @click="switchViewMode('week')"
              >
                {{ t('activities.viewMode.week') }}
              </button>
            </div>

            <Button variant="outline" size="sm" @click="goToToday">
              {{ t('activities.today') }}
            </Button>
          </div>
        </div>

        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-2">
            <Button
              variant="ghost"
              size="sm"
              @click="viewMode === 'day' ? goToPreviousDay() : goToPreviousWeek()"
            >
              <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M15 19l-7-7 7-7"
                />
              </svg>
            </Button>
            <h2 class="text-base font-semibold text-gray-900 min-w-[200px] text-center">
              {{ viewMode === 'day' ? getDateLabel : getWeekLabel }}
            </h2>
            <Button
              variant="ghost"
              size="sm"
              @click="viewMode === 'day' ? goToNextDay() : goToNextWeek()"
            >
              <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 5l7 7-7 7"
                />
              </svg>
            </Button>
          </div>
        </div>
      </div>

      <!-- Timer section -->
      <div class="px-4 py-3 border-b border-gray-200 bg-white">
        <ActivityTimer
          v-if="timerStore.isRunning"
          :category-name="activeTimerCategoryName"
          @stop="handleTimerStop"
        />
        <Button v-else size="lg" class="w-full" @click="handleStartTimerClick">
          {{ t('activities.timer.startButton') }}
        </Button>
      </div>

      <div class="flex-1 overflow-auto bg-gray-50">
        <!-- Day View -->
        <div v-if="viewMode === 'day'" class="max-w-4xl mx-auto p-4">
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 relative">
            <!-- Header -->
            <div class="grid grid-cols-[80px_1fr] border-b border-gray-200">
              <div class="border-r border-gray-200"></div>
              <div class="px-4 py-2 text-sm font-semibold text-gray-600">
                {{ t('activities.schedule') }}
              </div>
            </div>

            <!-- Timeline container -->
            <div class="relative">
              <!-- Time slots grid -->
              <div class="grid grid-cols-[80px_1fr]">
                <template v-for="slot in timeSlots" :key="slot">
                  <div
                    class="text-right pr-3 py-3 text-xs text-gray-500 border-r border-gray-200 border-t border-gray-100"
                  >
                    {{ slot }}
                  </div>
                  <div
                    class="min-h-[60px] transition-colors border-t border-gray-100"
                    :class="
                      timerStore.isRunning
                        ? 'cursor-not-allowed opacity-50'
                        : 'hover:bg-primary-50/30 cursor-pointer'
                    "
                    @click="timerStore.isRunning ? undefined : handleTimeSlotClick(slot)"
                  ></div>
                </template>
              </div>

              <!-- Activities overlay -->
              <div class="absolute top-0 left-[80px] right-0 h-full pointer-events-none">
                <div class="relative h-[1440px]">
                  <!-- 15-minute snap guides (subtle) -->
                  <div
                    v-for="marker in quarterHourMarkers"
                    :key="`quarter-${marker}`"
                    class="absolute left-0 right-0 border-t border-dashed border-gray-200 opacity-30"
                    :style="{ top: `${marker}px` }"
                  ></div>

                  <!-- Activity blocks -->
                  <div
                    v-for="activity in activitiesStore.activities"
                    :key="activity.id"
                    :data-activity-id="activity.id"
                    class="group absolute left-0 right-0 mx-1 rounded-md px-2 py-1 text-xs text-white font-medium overflow-hidden shadow-sm cursor-move hover:shadow transition-shadow pointer-events-auto select-none z-10"
                    :style="getActivityStyle(activity)"
                    @mousedown="handleDragStart(activity, $event)"
                    @click="handleActivityClick(activity)"
                    @mouseenter="handleActivityMouseEnter(activity, $event)"
                    @mouseleave="handleActivityMouseLeave"
                  >
                    <!-- Resize handle top -->
                    <div
                      class="absolute top-0 left-0 right-0 h-2 cursor-ns-resize opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center"
                      @mousedown="handleResizeStart(activity, 'top', $event)"
                    >
                      <div class="w-8 h-1 bg-white/40 rounded-full"></div>
                    </div>

                    <template v-if="shouldShowText(activity)">
                      <div class="font-semibold flex items-center gap-1.5">
                        <svg
                          v-if="activity.isFromTask"
                          class="w-3 h-3 opacity-75 flex-shrink-0"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                          />
                        </svg>
                        <span class="truncate">{{ getActivityDisplayName(activity) }}</span>
                      </div>
                      <div v-if="activity.isFromTask" class="flex items-center gap-1 mt-0.5">
                        <span
                          class="inline-flex items-center px-1.5 py-0 rounded-full text-[10px] font-medium"
                          :style="{
                            backgroundColor: getCategoryColor(activity.categoryId) + '33',
                            color: getCategoryColor(activity.categoryId),
                          }"
                        >
                          {{ getCategoryName(activity.categoryId) }}
                        </span>
                      </div>
                      <div class="text-xs opacity-90">
                        {{ activity.startTime }} -
                        {{ activity.endTime ?? t('activities.timer.running') }}
                      </div>
                      <div v-if="activity.notes" class="text-xs opacity-75 truncate">
                        {{ activity.notes }}
                      </div>
                    </template>

                    <!-- Resize handle bottom -->
                    <div
                      class="absolute bottom-0 left-0 right-0 h-2 cursor-ns-resize opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center"
                      @mousedown="handleResizeStart(activity, 'bottom', $event)"
                    >
                      <div class="w-8 h-1 bg-white/40 rounded-full"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Week View -->
        <div v-else class="max-w-7xl mx-auto p-4">
          <div
            class="bg-white rounded-lg shadow-sm border border-gray-200 relative overflow-x-auto"
          >
            <!-- Header with days -->
            <div class="grid grid-cols-[80px_repeat(7,minmax(120px,1fr))] border-b border-gray-200">
              <div class="border-r border-gray-200"></div>
              <div
                v-for="(date, index) in getWeekDates"
                :key="index"
                class="px-2 py-2 text-center border-r border-gray-200 last:border-r-0"
              >
                <div class="text-xs font-semibold text-gray-600 uppercase">
                  {{ date.toLocaleDateString('fr-FR', { weekday: 'short' }) }}
                </div>
                <div class="text-sm font-medium text-gray-900">
                  {{ date.getDate() }}
                </div>
              </div>
            </div>

            <!-- Timeline container -->
            <div class="relative">
              <!-- Time slots grid -->
              <div class="grid grid-cols-[80px_repeat(7,minmax(120px,1fr))]">
                <template v-for="slot in timeSlots" :key="slot">
                  <div
                    class="text-right pr-3 py-3 text-xs text-gray-500 border-r border-gray-200 border-t border-gray-100 sticky left-0 bg-white z-10"
                  >
                    {{ slot }}
                  </div>
                  <div
                    v-for="(date, dayIndex) in getWeekDates"
                    :key="`${slot}-${dayIndex}`"
                    class="relative min-h-[60px] transition-colors border-t border-gray-100 border-r border-gray-50 last:border-r-0"
                    :class="
                      timerStore.isRunning
                        ? 'cursor-not-allowed opacity-50'
                        : 'hover:bg-primary-50/30 cursor-pointer'
                    "
                    @click="timerStore.isRunning ? undefined : handleWeekTimeSlotClick(date, slot)"
                  >
                    <!-- Activities overlay for this cell's day - only render on first time slot -->
                    <div
                      v-if="slot === '00:00'"
                      class="absolute top-0 left-0 right-0 pointer-events-none"
                      style="height: 1440px"
                    >
                      <!-- 15-minute snap guides -->
                      <div
                        v-for="marker in quarterHourMarkers"
                        :key="`week-quarter-${dayIndex}-${marker}`"
                        class="absolute left-0 right-0 border-t border-dashed border-gray-200 opacity-20"
                        :style="{ top: `${marker}px` }"
                      ></div>

                      <!-- Activity blocks for this day -->
                      <div
                        v-for="activity in getActivitiesForDate(date)"
                        :key="`week-${activity.id}`"
                        :data-activity-id="activity.id"
                        class="group absolute left-0 right-0 mx-0.5 rounded-md px-1.5 py-1 text-xs text-white font-medium overflow-hidden shadow-sm cursor-move hover:shadow transition-shadow pointer-events-auto select-none z-10"
                        :style="getActivityStyle(activity)"
                        @mousedown="handleDragStart(activity, $event)"
                        @click="handleActivityClick(activity)"
                        @mouseenter="handleActivityMouseEnter(activity, $event)"
                        @mouseleave="handleActivityMouseLeave"
                      >
                        <!-- Resize handle top -->
                        <div
                          class="absolute top-0 left-0 right-0 h-2 cursor-ns-resize opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center"
                          @mousedown="handleResizeStart(activity, 'top', $event)"
                        >
                          <div class="w-6 h-0.5 bg-white/40 rounded-full"></div>
                        </div>

                        <template v-if="shouldShowText(activity)">
                          <div
                            class="font-semibold text-xs leading-tight truncate flex items-center gap-1"
                          >
                            <svg
                              v-if="activity.isFromTask"
                              class="w-2.5 h-2.5 opacity-75 flex-shrink-0"
                              fill="none"
                              viewBox="0 0 24 24"
                              stroke="currentColor"
                            >
                              <path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"
                                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                              />
                            </svg>
                            <span class="truncate">{{ getActivityDisplayName(activity) }}</span>
                          </div>
                          <div class="text-xs opacity-90 truncate">
                            {{ activity.startTime }}
                          </div>
                        </template>

                        <!-- Resize handle bottom -->
                        <div
                          class="absolute bottom-0 left-0 right-0 h-2 cursor-ns-resize opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center"
                          @mousedown="handleResizeStart(activity, 'bottom', $event)"
                        >
                          <div class="w-6 h-0.5 bg-white/40 rounded-full"></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </template>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <ActivityDialog
      v-model:open="isActivityDialogOpen"
      :date="formattedDate"
      :initial-start-time="clickedTimeSlot || '09:00'"
      :activity="getEditingActivity"
      @save="handleSaveActivity"
      @delete="handleDeleteActivity"
    />

    <CategorySelector v-model:open="isCategorySelectorOpen" @select="handleCategorySelected" />

    <ActiveTimerDialog
      v-model:open="isActiveTimerDialogOpen"
      :category-name="activeTimerCategoryName"
      :start-time="timerStore.activeActivity?.startTime ?? ''"
      :elapsed-formatted="timerStore.elapsedFormatted"
      @continue="handleTimerContinue"
      @stop-now="handleTimerStopNow"
      @stop-at="handleTimerStopAt"
    />

    <!-- Global tooltip portal -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition-opacity duration-150"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition-opacity duration-100"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div
          v-if="hoveredActivity && getHoveredActivity"
          class="fixed z-50 pointer-events-none"
          :style="{
            left: `${tooltipPosition.x}px`,
            top: `${tooltipPosition.y}px`,
            transform: 'translateY(-50%)',
          }"
        >
          <div
            class="bg-gray-900 text-white text-xs rounded-lg px-3 py-2 shadow-lg max-w-xs whitespace-normal"
          >
            <div class="space-y-1">
              <div class="font-semibold flex items-center gap-1.5">
                <svg
                  v-if="getHoveredActivity.isFromTask"
                  class="w-3 h-3 opacity-75"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                {{ getActivityDisplayName(getHoveredActivity) }}
              </div>
              <div v-if="getHoveredActivity.isFromTask" class="text-xs opacity-80">
                <span
                  class="inline-flex items-center px-1.5 py-0.5 rounded-full text-[10px] font-medium"
                  :style="{
                    backgroundColor: getCategoryColor(getHoveredActivity.categoryId) + '33',
                    color: getCategoryColor(getHoveredActivity.categoryId),
                  }"
                >
                  {{ getCategoryName(getHoveredActivity.categoryId) }}
                </span>
              </div>
              <div class="text-xs opacity-90">
                {{ getHoveredActivity.startTime }} -
                {{ getHoveredActivity.endTime ?? t('activities.timer.running') }}
                <span class="opacity-75">({{ getActivityDuration(getHoveredActivity) }})</span>
              </div>
              <div
                v-if="getHoveredActivity.notes"
                class="text-xs opacity-75 border-t border-white/20 pt-1 mt-1"
              >
                {{ getHoveredActivity.notes }}
              </div>
            </div>
          </div>
          <!-- Arrow -->
          <div
            class="absolute right-full top-1/2 -translate-y-1/2 w-0 h-0 border-4 border-r-gray-900 border-y-transparent border-l-transparent"
          ></div>
        </div>
      </Transition>
    </Teleport>
  </AuthenticatedLayout>
</template>
