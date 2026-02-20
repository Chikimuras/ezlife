<script setup lang="ts">
import { computed, inject, type Ref } from 'vue'

interface Props {
  placeholder?: string
}

const props = defineProps<Props>()

const selectedValue = inject<Ref<string>>('selectValue')
const selectedLabel = inject<Ref<string>>('selectLabel')

const displayValue = computed(() => {
  if (selectedLabel?.value) return selectedLabel.value
  if (selectedValue?.value) return selectedValue.value
  return props.placeholder || 'Select...'
})
</script>

<template>
  <span>{{ displayValue }}</span>
</template>
