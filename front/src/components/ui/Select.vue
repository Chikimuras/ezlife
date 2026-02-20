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
const selectedLabel = ref('')
const isOpen = ref(false)
const labelMap = ref<Map<string, string>>(new Map())

watch(
  () => props.modelValue,
  (newVal) => {
    if (newVal !== undefined) {
      selectedValue.value = newVal
      selectedLabel.value = labelMap.value.get(newVal) ?? ''
    }
  },
)

watch(selectedValue, (newVal) => {
  emit('update:modelValue', newVal)
})

provide('selectValue', selectedValue)
provide('selectLabel', selectedLabel)
provide('selectOpen', isOpen)

const registerLabel = (value: string, label: string) => {
  labelMap.value.set(value, label)
  if (value === selectedValue.value && !selectedLabel.value) {
    selectedLabel.value = label
  }
}

provide('registerLabel', registerLabel)

const selectItem = (value: string, label?: string) => {
  selectedValue.value = value
  selectedLabel.value = label ?? labelMap.value.get(value) ?? value
  isOpen.value = false
}

provide('selectItem', selectItem)
</script>

<template>
  <div class="relative">
    <slot />
  </div>
</template>
