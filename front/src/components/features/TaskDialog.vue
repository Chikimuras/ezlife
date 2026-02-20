<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useTasksStore } from '@/stores/tasks'
import { useCategoriesStore } from '@/stores/categories'
import type { Task, CreateTask } from '@/lib/api/schemas/task'
import Dialog from '@/components/ui/Dialog.vue'
import DialogContent from '@/components/ui/DialogContent.vue'
import DialogHeader from '@/components/ui/DialogHeader.vue'
import DialogTitle from '@/components/ui/DialogTitle.vue'
import DialogFooter from '@/components/ui/DialogFooter.vue'
import Button from '@/components/ui/Button.vue'
import FloatingInput from '@/components/ui/FloatingInput.vue'
import FloatingSelect from '@/components/ui/FloatingSelect.vue'
import FloatingTextarea from '@/components/ui/FloatingTextarea.vue'
import RRuleEditor from '@/components/features/RRuleEditor.vue'

const props = defineProps<{
  open: boolean
  task?: Task
  taskListId: string
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  saved: [task: Task]
  close: []
}>()

const { t } = useI18n()
const tasksStore = useTasksStore()
const categoriesStore = useCategoriesStore()

interface CreateTaskForm extends CreateTask {
  exdates: string[]
}

const formData = ref<CreateTaskForm>({
  taskListId: props.taskListId,
  title: '',
  description: '',
  priority: 'medium',
  categoryId: undefined,
  dueDate: undefined,
  scheduledDate: undefined,
  scheduledStartTime: undefined,
  scheduledEndTime: undefined,
  estimatedDurationMinutes: undefined,
  recurrenceRule: undefined,
  position: 0,
  exdates: [],
})

const priorities = ['low', 'medium', 'high', 'urgent'] as const

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      if (props.task) {
        formData.value = {
          taskListId: props.task.taskListId,
          title: props.task.title,
          description: props.task.description ?? undefined,
          priority: props.task.priority,
          categoryId: props.task.categoryId ?? undefined,
          dueDate: props.task.dueDate ?? undefined,
          scheduledDate: props.task.scheduledDate ?? undefined,
          scheduledStartTime: props.task.scheduledStartTime ?? undefined,
          scheduledEndTime: props.task.scheduledEndTime ?? undefined,
          estimatedDurationMinutes: props.task.estimatedDurationMinutes ?? undefined,
          recurrenceRule: props.task.recurrenceRule ?? undefined,
          position: props.task.position,
          exdates: [], // TODO: Load exdates from task when supported by backend
        }
      } else {
        formData.value = {
          taskListId: props.taskListId,
          title: '',
          description: '',
          priority: 'medium',
          categoryId: undefined,
          dueDate: undefined,
          scheduledDate: undefined,
          scheduledStartTime: undefined,
          scheduledEndTime: undefined,
          estimatedDurationMinutes: undefined,
          recurrenceRule: undefined,
          position: 0,
          exdates: [],
        }
      }
    }
  },
)

// Auto-calculate end time from start time + estimated duration
watch(
  [() => formData.value.scheduledStartTime, () => formData.value.estimatedDurationMinutes],
  ([startTime, duration]) => {
    if (startTime && duration && duration > 0) {
      const [h, m] = startTime.split(':').map(Number)
      const totalMin = (h ?? 0) * 60 + (m ?? 0) + duration
      const endH = Math.floor(totalMin / 60) % 24
      const endM = totalMin % 60
      formData.value.scheduledEndTime = `${String(endH).padStart(2, '0')}:${String(endM).padStart(2, '0')}`
    }
  },
)

const showEndTime = computed(() => !formData.value.estimatedDurationMinutes || formData.value.estimatedDurationMinutes <= 0)

const handleSubmit = async () => {
  try {
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { exdates, categoryId, ...rest } = formData.value
    const payload = {
      ...rest,
      categoryId: categoryId === 'unassigned' ? undefined : categoryId,
    }
    let savedTask: Task
    if (props.task) {
      savedTask = await tasksStore.updateTask(props.task.id, payload)
    } else {
      savedTask = await tasksStore.createTask(payload)
    }
    emit('saved', savedTask)
    emit('update:open', false)
  } catch (error) {
    // Error is handled by store
    console.error(error)
  }
}


</script>

<template>
  <Dialog :open="open" @update:open="emit('update:open', $event)">
    <DialogContent class="sm:max-w-[600px]">
      <DialogHeader>
        <DialogTitle>{{ task ? t('tasks.editTask') : t('tasks.newTask') }}</DialogTitle>
      </DialogHeader>

      <form @submit.prevent="handleSubmit" class="grid gap-4 py-4 max-h-[80vh] overflow-y-auto px-1">
        <!-- Title -->
        <FloatingInput
          v-model="formData.title"
          :label="t('tasks.taskTitle')"
          required
        />

        <!-- Description -->
        <FloatingTextarea
          v-model="formData.description"
          :label="t('tasks.description')"
          class="min-h-[100px]"
        />

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Task List -->
          <FloatingSelect
            v-model="formData.taskListId"
            :label="t('tasks.taskLists')"
            :options="tasksStore.taskLists.map(l => ({ value: l.id, label: l.name }))"
          />

          <!-- Category -->
          <FloatingSelect
            v-model="formData.categoryId"
            :label="t('tasks.category')"
            :options="[
              { value: 'unassigned', label: t('common.no') },
              ...categoriesStore.categories.map(c => ({ value: c.id, label: c.name }))
            ]"
            :placeholder="t('activities.fields.categoryPlaceholder')"
          />
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
           <!-- Priority -->
          <FloatingSelect
            v-model="formData.priority"
            :label="t('tasks.priority')"
            :options="priorities.map(p => ({ value: p, label: t(`tasks.priorities.${p}`) }))"
          />

           <!-- Estimated Duration -->
          <FloatingInput
            v-model.number="formData.estimatedDurationMinutes"
            :label="`${t('tasks.estimatedDuration')} (${t('tasks.minutes')})`"
            type="number"
            min="0"
          />
        </div>

        <!-- Recurrence Editor -->
        <div class="col-span-full">
          <RRuleEditor
            v-model="formData.recurrenceRule"
            :exdates="formData.exdates"
            @update:exdates="formData.exdates = $event"
          />
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div v-if="!formData.recurrenceRule">
            <FloatingInput
              v-model="formData.dueDate"
              :label="t('tasks.dueDate')"
              type="date"
            />
          </div>

          <FloatingInput
            v-model="formData.scheduledDate"
            :label="formData.recurrenceRule ? t('tasks.startsFrom') : t('tasks.scheduledDate')"
            type="date"
          />
        </div>

        <div v-if="formData.scheduledDate" class="grid grid-cols-2 gap-4 bg-gray-50 p-3 rounded-lg border border-gray-100">
          <FloatingInput
            v-model="formData.scheduledStartTime"
            :label="t('activities.fields.startTime')"
            type="time"
            class="bg-white"
          />

          <div v-if="showEndTime">
            <FloatingInput
              v-model="formData.scheduledEndTime"
              :label="t('activities.fields.endTime')"
              type="time"
              class="bg-white"
            />
          </div>
          <div v-else class="flex items-center gap-2 text-sm text-gray-500">
            <span class="text-gray-400">{{ t('activities.fields.endTime') }} :</span>
            <span class="font-medium text-gray-700">{{ formData.scheduledEndTime || '--:--' }}</span>
            <span class="text-xs text-gray-400">({{ formData.estimatedDurationMinutes }} {{ t('tasks.minutes') }})</span>
          </div>
        </div>

      </form>

      <DialogFooter>
        <Button variant="outline" @click="emit('update:open', false)">
          {{ t('common.cancel') }}
        </Button>
        <Button @click="handleSubmit" :disabled="!formData.title">
          {{ t('common.save') }}
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
