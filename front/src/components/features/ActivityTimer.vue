<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useTimerStore } from '@/stores/timer'
import Button from '@/components/ui/Button.vue'

defineProps<{
  categoryName: string
}>()

const emit = defineEmits<{
  (e: 'stop'): void
}>()

const { t } = useI18n()
const timerStore = useTimerStore()

const handleStop = () => {
  emit('stop')
}
</script>

<template>
  <div
    class="bg-white border-2 border-primary-200 rounded-xl p-6 shadow-md flex flex-col items-center gap-4 animate-in fade-in slide-in-from-bottom-4 duration-500"
  >
    <!-- Running Badge -->
    <div
      class="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-primary-100 text-primary-700 uppercase tracking-wide"
    >
      <span class="relative flex h-2 w-2">
        <span
          class="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary-400 opacity-75"
        ></span>
        <span class="relative inline-flex rounded-full h-2 w-2 bg-primary-500"></span>
      </span>
      {{ t('activities.timer.running') }}
    </div>

    <!-- Timer Display -->
    <div class="text-center space-y-1">
      <div class="text-4xl font-bold text-primary-700 tabular-nums font-mono tracking-wider">
        {{ timerStore.elapsedFormatted }}
      </div>
      <div class="text-sm text-gray-600 font-medium">
        {{ categoryName }}
      </div>
    </div>

    <!-- Stop Button -->
    <Button
      variant="destructive"
      size="default"
      class="w-full sm:w-auto min-w-[140px]"
      @click="handleStop"
    >
      {{ t('activities.timer.stop') }}
    </Button>
  </div>
</template>
