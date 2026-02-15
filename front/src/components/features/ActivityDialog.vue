<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import Dialog from '@/components/ui/Dialog.vue'
import DialogContent from '@/components/ui/DialogContent.vue'
import DialogHeader from '@/components/ui/DialogHeader.vue'
import DialogTitle from '@/components/ui/DialogTitle.vue'
import DialogFooter from '@/components/ui/DialogFooter.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Label from '@/components/ui/Label.vue'
import Select from '@/components/ui/Select.vue'
import SelectTrigger from '@/components/ui/SelectTrigger.vue'
import SelectValue from '@/components/ui/SelectValue.vue'
import SelectContent from '@/components/ui/SelectContent.vue'
import SelectItem from '@/components/ui/SelectItem.vue'
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
        }
      } else {
        formData.value.date = props.date
        formData.value.startTime = props.initialStartTime

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
        <div class="grid gap-2">
          <Label for="category">{{ t('activities.fields.category') }}</Label>
          <Select v-model="formData.categoryId">
            <SelectTrigger>
              <SelectValue :placeholder="t('activities.fields.categoryPlaceholder')" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem
                v-for="category in categoriesStore.categories"
                :key="category.id"
                :value="category.id"
              >
                {{ category.name }}
              </SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div class="grid gap-2">
            <Label for="startTime">{{ t('activities.fields.startTime') }}</Label>
            <Input id="startTime" v-model="formData.startTime" type="time" />
          </div>

          <div class="grid gap-2">
            <Label for="endTime">{{ t('activities.fields.endTime') }}</Label>
            <Input id="endTime" v-model="formData.endTime" type="time" />
          </div>
        </div>

        <div class="grid gap-2">
          <Label for="notes">{{ t('activities.fields.notes') }}</Label>
          <Input
            id="notes"
            v-model="formData.notes"
            :placeholder="t('activities.fields.notesPlaceholder')"
          />
        </div>
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
