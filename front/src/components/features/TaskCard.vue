<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Task } from '@/lib/api/schemas/task'
import { cn } from '@/lib/utils/cn'
import Checkbox from '@/components/ui/Checkbox.vue'
import Badge from '@/components/ui/Badge.vue'
import { Calendar, CalendarCheck, Clock, Edit2, Trash2, ArrowRightCircle, Link as LinkIcon, Play, Undo2 } from 'lucide-vue-next'
import { useCategoriesStore } from '@/stores/categories'
import { useGroupsStore } from '@/stores/groups'

const props = defineProps<{
  task: Task
}>()

const emit = defineEmits<{
  complete: [task: Task]
  edit: [task: Task]
  delete: [task: Task]
  convertToActivity: [task: Task]
  statusChange: [task: Task, status: string]
}>()

const { t } = useI18n()
const categoriesStore = useCategoriesStore()
const groupsStore = useGroupsStore()

const category = computed(() => {
  if (!props.task.categoryId) return null
  return categoriesStore.categories.find(c => c.id === props.task.categoryId)
})

const group = computed(() => {
  const groupId = category.value?.groupId
  if (!groupId) return null
  return groupsStore.groups.find(g => g.id === groupId)
})

const priorityColor = computed(() => {
  switch (props.task.priority) {
    case 'urgent': return 'bg-red-100 text-red-700'
    case 'high': return 'bg-orange-100 text-orange-700'
    case 'medium': return 'bg-blue-100 text-blue-700'
    case 'low': return 'bg-green-100 text-green-700'
    default: return 'bg-gray-100 text-gray-700'
  }
})

const isDone = computed(() => props.task.status === 'done')
const isInProgress = computed(() => props.task.status === 'in_progress')

const handleCheckboxChange = () => {
  emit('complete', props.task)
}

const formattedDueDate = computed(() => {
  if (!props.task.dueDate) return null
  return new Date(props.task.dueDate).toLocaleDateString()
})

const formattedScheduledDate = computed(() => {
  if (!props.task.scheduledDate) return null
  return new Date(props.task.scheduledDate).toLocaleDateString()
})

const isOverdue = computed(() => {
  if (!props.task.dueDate || isDone.value) return false
  return new Date(props.task.dueDate) < new Date()
})
</script>

<template>
  <div
    class="group relative flex flex-col gap-2 rounded-lg border border-gray-200 bg-white p-3 shadow-sm transition-all hover:shadow-md"
    :class="{ 'opacity-60 transform scale-95': isDone, 'border-primary-200 bg-primary-50/10': isInProgress }"
  >
    <div class="flex items-start justify-between gap-3">
      <div class="flex items-start gap-3 flex-1 min-w-0">
        <Checkbox
          :checked="isDone"
          @update:checked="handleCheckboxChange"
          :class="cn('mt-1 flex-shrink-0', { 'border-primary-500 text-primary-600': isInProgress && !isDone })"
        />
        <div class="flex flex-col min-w-0 flex-1">
          <div class="flex items-center gap-2 mb-1 flex-wrap">
             <span
              class="text-sm font-medium text-gray-900 break-words"
              :class="{ 'line-through text-gray-500': isDone }"
            >
              {{ task.title }}
            </span>
             <LinkIcon
              v-if="task.activityIds.length > 0"
              class="h-3 w-3 text-primary-500"
              :title="t('tasks.addedToTracker')"
            />
          </div>
          
          <div class="flex flex-wrap items-center gap-2 text-xs text-gray-500">
            <Badge
              v-if="task.priority !== 'medium' || isInProgress" 
              class="px-1.5 py-0 text-[10px]"
              :class="priorityColor"
            >
              {{ t(`tasks.priorities.${task.priority}`) }}
            </Badge>
            
             <span v-if="formattedScheduledDate" class="flex items-center gap-1 text-primary-600">
              <CalendarCheck class="h-3 w-3" />
              {{ formattedScheduledDate }}
            </span>

            <span v-if="formattedDueDate" class="flex items-center gap-1" :class="{ 'text-red-500': isOverdue }">
              <Calendar class="h-3 w-3" />
              {{ formattedDueDate }}
            </span>
            
            <span v-if="task.estimatedDurationMinutes" class="flex items-center gap-1">
              <Clock class="h-3 w-3" />
              {{ task.estimatedDurationMinutes }}m
            </span>

             <span
              v-if="category"
              class="flex items-center gap-1 rounded px-1.5 py-0.5"
              :style="{ backgroundColor: (group?.color || '#a855f7') + '20', color: group?.color || '#a855f7' }"
            >
              {{ category.name }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Hover Actions -->
    <div
      class="absolute right-2 top-2 flex items-center gap-1 rounded-md bg-white/90 p-1 shadow-sm opacity-0 transition-opacity duration-200 pointer-events-none group-hover:opacity-100 group-hover:pointer-events-auto"
    >
      <button
        v-if="isDone"
        @click.stop="emit('statusChange', task, 'todo')"
        class="p-1 text-gray-400 hover:text-orange-500 rounded"
        :title="t('tasks.statuses.todo')"
      >
        <Undo2 class="h-4 w-4" />
      </button>
      <button
        v-if="!isInProgress && !isDone"
        @click.stop="emit('statusChange', task, 'in_progress')"
        class="p-1 text-gray-400 hover:text-primary-600 rounded"
        :title="t('tasks.statuses.in_progress')"
      >
        <Play class="h-4 w-4" />
      </button>
      <button
        v-if="!isDone"
        @click.stop="emit('convertToActivity', task)"
        class="p-1 text-gray-400 hover:text-primary-600 rounded"
        :title="t('tasks.convertToActivity')"
      >
        <ArrowRightCircle class="h-4 w-4" />
      </button>
      <button
        @click.stop="emit('edit', task)"
        class="p-1 text-gray-400 hover:text-primary-600 rounded"
        :title="t('common.edit')"
      >
        <Edit2 class="h-4 w-4" />
      </button>
      <button
        @click.stop="emit('delete', task)"
        class="p-1 text-gray-400 hover:text-red-600 rounded"
        :title="t('common.delete')"
      >
        <Trash2 class="h-4 w-4" />
      </button>
    </div>
  </div>
</template>
