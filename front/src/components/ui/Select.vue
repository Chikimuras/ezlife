<script setup lang="ts">
import { provide, ref, watch } from 'vue'

interface Props {
  modelValue?: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const selectedValue = ref(props.modelValue ?? '')
const isOpen = ref(false)

watch(
  () => props.modelValue,
  (newVal) => {
    if (newVal !== undefined) {
      selectedValue.value = newVal
    }
  },
)

watch(selectedValue, (newVal) => {
  emit('update:modelValue', newVal)
})

provide('selectValue', selectedValue)
provide('selectOpen', isOpen)

const selectItem = (value: string) => {
  selectedValue.value = value
  isOpen.value = false
}

provide('selectItem', selectItem)
</script>

<template>
  <div class="relative">
    <slot />
  </div>
</template>
