<script setup lang="ts">
import { provide, ref, watch } from 'vue'

interface Props {
  defaultValue?: string
  modelValue?: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const activeTab = ref(props.modelValue ?? props.defaultValue ?? '')

watch(
  () => props.modelValue,
  (newVal) => {
    if (newVal !== undefined) {
      activeTab.value = newVal
    }
  },
)

watch(activeTab, (newVal) => {
  emit('update:modelValue', newVal)
})

provide('activeTab', activeTab)
</script>

<template>
  <div class="w-full">
    <slot />
  </div>
</template>
