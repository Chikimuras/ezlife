<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import Dialog from '@/components/ui/Dialog.vue'
import DialogContent from '@/components/ui/DialogContent.vue'
import DialogHeader from '@/components/ui/DialogHeader.vue'
import DialogTitle from '@/components/ui/DialogTitle.vue'
import DialogFooter from '@/components/ui/DialogFooter.vue'
import Button from '@/components/ui/Button.vue'
import FloatingInput from '@/components/ui/FloatingInput.vue'
import FloatingSelect from '@/components/ui/FloatingSelect.vue'
import { useCategoriesStore } from '@/stores/categories'
import type { CreateActivity, Activity } from '@/lib/api/schemas/activity'

const { t } = useI18n()
const categoriesStore = useCategoriesStore()

interface Props {
  open: boolean
  date: string
  initialStartTime?: string
  activity?: Activity | null
}

const props = withDefaults(defineProps<Props>(), {
  initialStartTime: '09:00',
  activity: null,
})

const emit = defineEmits<{
  'update:open': [value: boolean]
  save: [data: CreateActivity]
  delete: [activityId: string]
}>()

const formData = ref<CreateActivity>({
  date: props.date,
  startTime: props.initialStartTime,
  endTime: '',
  categoryId: '',
  notes: '',
  taskId: null,
  isFromTask: false,
})

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      if (props.activity) {
        formData.value = {
          date: props.activity.date,
          startTime: props.activity.startTime,
          endTime: props.activity.endTime,
          categoryId: props.activity.categoryId,
          notes: props.activity.notes ?? '',
          taskId: props.activity.taskId ?? null,
          isFromTask: props.activity.isFromTask ?? false,
        }
      } else {
        formData.value.date = props.date
        formData.value.startTime = props.initialStartTime
        formData.value.taskId = null
        formData.value.isFromTask = false

        const [hours, minutes] = props.initialStartTime.split(':')
        const endHour = (parseInt(hours ?? '0') + 1).toString().padStart(2, '0')
        formData.value.endTime = `${endHour}:${minutes ?? '00'}`

        if (!formData.value.categoryId && categoriesStore.categories.length > 0) {
          formData.value.categoryId = categoriesStore.categories[0]?.id ?? ''
        }
      }
    }
  },
)

const handleSave = () => {
  emit('save', formData.value)
  emit('update:open', false)
}

const handleCancel = () => {
  emit('update:open', false)
}

const handleDelete = () => {
  if (props.activity?.id) {
    emit('delete', props.activity.id)
  }
}
</script>

<template>
  <Dialog :open="open" @update:open="emit('update:open', $event)">
    <DialogContent>
      <DialogHeader>
        <DialogTitle>{{ activity ? t('activities.edit') : t('activities.add') }}</DialogTitle>
      </DialogHeader>

      <div class="grid gap-4 py-4">
        <FloatingSelect
          v-model="formData.categoryId"
          :label="t('activities.fields.category')"
          :placeholder="t('activities.fields.categoryPlaceholder')"
          :options="categoriesStore.categories.map(c => ({ value: c.id, label: c.name }))"
        />

        <div class="grid grid-cols-2 gap-4">
          <FloatingInput
            v-model="formData.startTime"
            :label="t('activities.fields.startTime')"
            type="time"
          />

          <FloatingInput
            v-model="formData.endTime"
            :label="t('activities.fields.endTime')"
            type="time"
          />
        </div>

        <FloatingInput
          v-model="formData.notes"
          :label="t('activities.fields.notes')"
          :placeholder="t('activities.fields.notesPlaceholder')"
        />
      </div>

      <DialogFooter>
        <div class="flex items-center justify-between w-full">
          <Button v-if="activity" variant="destructive" @click="handleDelete">
            {{ t('common.delete') }}
          </Button>
          <div class="flex items-center gap-2" :class="{ 'ml-auto': !activity }">
            <Button variant="outline" @click="handleCancel">{{ t('common.cancel') }}</Button>
            <Button @click="handleSave">{{ t('common.save') }}</Button>
          </div>
        </div>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
