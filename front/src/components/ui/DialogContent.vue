<script setup lang="ts">
import { inject, type Ref, computed } from 'vue'
import { cn } from '@/lib/utils/cn'

interface Props {
  class?: string
}

const props = defineProps<Props>()

const dialogOpen = inject<Ref<boolean>>('dialogOpen')
const closeDialog = inject<(() => void) | undefined>('closeDialog')

const isDialogOpen = computed(() => dialogOpen?.value === true)

const handleBackdropClick = () => {
  if (closeDialog) {
    closeDialog()
  }
}
</script>

<template>
  <Teleport to="body">
    <div v-if="isDialogOpen" class="fixed inset-0 z-50 flex items-center justify-center">
      <div class="fixed inset-0 bg-gray-900/20 backdrop-blur-sm" @click="handleBackdropClick" />
      <div
        :class="
          cn(
            'relative z-50 w-full max-w-lg bg-white border border-gray-100 rounded-2xl p-8 shadow-xl',
            props.class,
          )
        "
      >
        <slot />
      </div>
    </div>
  </Teleport>
</template>
