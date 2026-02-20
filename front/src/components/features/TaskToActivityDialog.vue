<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Task, ConvertToActivity } from '@/lib/api/schemas/task'
import { useTasksStore } from '@/stores/tasks'
import { useCategoriesStore } from '@/stores/categories'
import Dialog from '@/components/ui/Dialog.vue'
import DialogContent from '@/components/ui/DialogContent.vue'
import DialogHeader from '@/components/ui/DialogHeader.vue'
import DialogTitle from '@/components/ui/DialogTitle.vue'
import DialogFooter from '@/components/ui/DialogFooter.vue'
import Button from '@/components/ui/Button.vue'
import FloatingInput from '@/components/ui/FloatingInput.vue'
import FloatingSelect from '@/components/ui/FloatingSelect.vue'

const props = defineProps<{
  open: boolean
  task: Task
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  saved: []
}>()

const { t } = useI18n()
const tasksStore = useTasksStore()
const categoriesStore = useCategoriesStore()

const formData = ref<ConvertToActivity>({
  date: new Date().toISOString().split('T')[0] ?? '',
  startTime: '09:00',
  endTime: '09:30',
  categoryId: undefined,
  notes: '',
})

const prefillFromTask = () => {
  if (!props.task) return

  const task = props.task
  formData.value.date = task.scheduledDate || (new Date().toISOString().split('T')[0] ?? '')

  if (task.scheduledStartTime) {
    formData.value.startTime = task.scheduledStartTime.substring(0, 5)
    if (task.scheduledEndTime) {
      formData.value.endTime = task.scheduledEndTime.substring(0, 5)
    } else if (task.estimatedDurationMinutes) {
      const [h, m] = formData.value.startTime.split(':').map(Number)
      const totalMin = (h ?? 0) * 60 + (m ?? 0) + task.estimatedDurationMinutes
      const endH = Math.floor(totalMin / 60) % 24
      const endM = totalMin % 60
      formData.value.endTime = `${String(endH).padStart(2, '0')}:${String(endM).padStart(2, '0')}`
    } else {
      const [h, m] = formData.value.startTime.split(':').map(Number)
      const totalMin = (h ?? 0) * 60 + (m ?? 0) + 30
      formData.value.endTime = `${String(Math.floor(totalMin / 60) % 24).padStart(2, '0')}:${String(totalMin % 60).padStart(2, '0')}`
    }
  } else if (task.estimatedDurationMinutes) {
    const now = new Date()
    formData.value.startTime = now.toTimeString().substring(0, 5)
    const totalMin = now.getHours() * 60 + now.getMinutes() + task.estimatedDurationMinutes
    const endH = Math.floor(totalMin / 60) % 24
    const endM = totalMin % 60
    formData.value.endTime = `${String(endH).padStart(2, '0')}:${String(endM).padStart(2, '0')}`
  } else {
    const now = new Date()
    formData.value.startTime = now.toTimeString().substring(0, 5)
    const end = new Date(now.getTime() + 30 * 60000)
    formData.value.endTime = end.toTimeString().substring(0, 5)
  }

  formData.value.categoryId = task.categoryId || undefined
  formData.value.notes = task.description || task.title
}

watch(() => props.open, (isOpen) => {
  if (isOpen) prefillFromTask()
})

watch(() => props.task, () => {
  if (props.open) prefillFromTask()
})

const handleSubmit = async () => {
  try {
    // If no category selected but one exists in store, maybe warn or require it?
    // Schema says categoryId is optional.
    await tasksStore.convertToActivity(props.task.id, formData.value)
    emit('saved')
    emit('update:open', false)
  } catch (error) {
    console.error(error)
  }
}
</script>

<template>
  <Dialog :open="open" @update:open="emit('update:open', $event)">
    <DialogContent class="sm:max-w-[500px]">
      <DialogHeader>
        <DialogTitle>{{ t('tasks.convertDialog.title') }}</DialogTitle>
      </DialogHeader>

      <div class="grid gap-4 py-4">
        <p class="text-sm text-gray-500 mb-2">
           {{ t('tasks.convertDialog.description') }}
        </p>

        <FloatingInput
          v-model="formData.date"
          :label="t('tasks.completeDialog.date')"
          type="date"
          required
        />

        <div class="grid grid-cols-2 gap-4">
          <FloatingInput
            v-model="formData.startTime"
            :label="t('tasks.completeDialog.startTime')"
            type="time"
            required
          />
          <FloatingInput
            v-model="formData.endTime"
            :label="t('tasks.completeDialog.endTime')"
            type="time"
            required
          />
        </div>

        <FloatingSelect
          v-model="formData.categoryId"
          :label="t('tasks.category')"
          :placeholder="t('activities.fields.categoryPlaceholder')"
          :options="categoriesStore.categories.map(c => ({ value: c.id, label: c.name }))"
        />

        <FloatingInput
          v-model="formData.notes"
          :label="t('tasks.completeDialog.notes')"
        />
      </div>

      <DialogFooter>
        <Button variant="outline" @click="emit('update:open', false)">
          {{ t('common.cancel') }}
        </Button>
        <Button @click="handleSubmit">
          {{ t('common.save') }}
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
