<script setup lang="ts">
import { provide, ref, watch } from 'vue'

interface Props {
  open?: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:open': [value: boolean]
}>()

const isOpen = ref(props.open ?? false)

watch(
  () => props.open,
  (newVal) => {
    if (newVal !== undefined) {
      isOpen.value = newVal
    }
  },
)

watch(isOpen, (newVal) => {
  emit('update:open', newVal)
})

provide('dialogOpen', isOpen)

const closeDialog = () => {
  isOpen.value = false
}

provide('closeDialog', closeDialog)
</script>

<template>
  <slot />
</template>
