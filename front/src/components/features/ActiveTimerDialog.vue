<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Dialog from '@/components/ui/Dialog.vue'
import DialogContent from '@/components/ui/DialogContent.vue'
import DialogHeader from '@/components/ui/DialogHeader.vue'
import DialogTitle from '@/components/ui/DialogTitle.vue'
import Button from '@/components/ui/Button.vue'

interface Props {
  open: boolean
  categoryName: string
  startTime: string
  elapsedFormatted: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  continue: []
  stopNow: []
  stopAt: [endTime: string]
}>()

const { t } = useI18n()
const customEndTime = ref('')

const handleOpenUpdate = (val: boolean) => {
  if (!val && props.open) {
    emit('continue')
  }
  emit('update:open', val)
}

const isOpen = computed({
  get: () => props.open,
  set: (val) => handleOpenUpdate(val),
})

const handleContinue = () => {
  emit('continue')
  emit('update:open', false)
}

const handleStopNow = () => {
  emit('stopNow')
  emit('update:open', false)
}

const handleStopAt = () => {
  if (customEndTime.value) {
    emit('stopAt', customEndTime.value)
    emit('update:open', false)
  }
}

watch(
  () => props.open,
  (newVal) => {
    if (newVal) {
      const now = new Date()
      const hours = String(now.getHours()).padStart(2, '0')
      const minutes = String(now.getMinutes()).padStart(2, '0')
      customEndTime.value = `${hours}:${minutes}`
    }
  },
  { immediate: true },
)
</script>

<template>
  <Dialog :open="isOpen" @update:open="(val) => (isOpen = val)">
    <DialogContent class="sm:max-w-md">
      <DialogHeader>
        <DialogTitle>{{ t('activities.timer.title') }}</DialogTitle>
      </DialogHeader>

      <!-- Info section -->
      <div class="bg-gray-50 rounded-lg p-3 space-y-2">
        <div class="flex justify-between items-center text-sm">
          <span class="text-gray-500">{{ t('activities.fields.category') }}</span>
          <span class="font-medium text-gray-900">{{ props.categoryName }}</span>
        </div>
        <div class="flex justify-between items-center text-sm">
          <span class="text-gray-500">{{ t('activities.fields.startTime') }}</span>
          <span class="font-medium text-gray-900">{{ props.startTime }}</span>
        </div>
        <div class="pt-2 border-t border-gray-100 flex justify-between items-center">
          <span class="text-gray-500">{{ t('activities.timer.elapsed') }}</span>
          <span class="font-mono text-xl font-semibold text-primary-600">
            {{ props.elapsedFormatted }}
          </span>
        </div>
      </div>

      <!-- Actions -->
      <div class="space-y-3 mt-2">
        <!-- Option 1: Continue -->
        <Button variant="default" class="w-full" @click="handleContinue">
          {{ t('activities.timer.yes') }}
        </Button>

        <!-- Option 2: Finish now -->
        <Button variant="outline" class="w-full" @click="handleStopNow">
          {{ t('activities.timer.finishNow') }}
        </Button>

        <!-- Option 3: Finish at specific time -->
        <div class="flex items-center gap-2">
          <Button variant="outline" class="shrink-0" @click="handleStopAt">
            {{ t('activities.timer.finishAt') }}
          </Button>
          <input
            type="time"
            v-model="customEndTime"
            class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
          />
        </div>
      </div>
    </DialogContent>
  </Dialog>
</template>
