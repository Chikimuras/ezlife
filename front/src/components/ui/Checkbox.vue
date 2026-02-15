<script setup lang="ts">
import { computed } from 'vue'
import { cn } from '@/lib/utils/cn'

interface Props {
  checked?: boolean
  disabled?: boolean
  class?: string
}

const props = withDefaults(defineProps<Props>(), {
  checked: false,
  disabled: false,
})

const emit = defineEmits<{
  'update:checked': [value: boolean]
}>()

const checkboxClass = computed(() =>
  cn(
    'w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500 transition-colors',
    props.class,
  ),
)
</script>

<template>
  <input
    type="checkbox"
    :class="checkboxClass"
    :checked="checked"
    :disabled="disabled"
    @change="emit('update:checked', ($event.target as HTMLInputElement).checked)"
  />
</template>
