<script setup lang="ts">
import { computed } from 'vue'
import { cn } from '@/lib/utils/cn'

interface Props {
  modelValue?: string | number
  label: string
  type?: string
  id?: string
  required?: boolean
  disabled?: boolean
  min?: string | number
  class?: string
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  disabled: false,
  required: false,
})

const emit = defineEmits<{
  'update:modelValue': [value: string | number]
}>()

const hasValue = computed(
  () => props.modelValue !== undefined && props.modelValue !== '' && props.modelValue !== null,
)

const inputId = computed(() => props.id ?? `fi-${props.label.replace(/\s/g, '-').toLowerCase()}`)
</script>

<template>
  <div :class="cn('relative', props.class)">
    <input
      :id="inputId"
      :type="type"
      :value="modelValue"
      :disabled="disabled"
      :required="required"
      :min="min"
      placeholder=" "
      class="peer w-full px-3 py-2 border border-gray-200 rounded-lg text-gray-900 focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all disabled:cursor-not-allowed disabled:opacity-50"
      @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
    />
    <label
      :for="inputId"
      class="absolute left-3 bg-white px-1 pointer-events-none transition-all duration-200 peer-placeholder-shown:top-2.5 peer-placeholder-shown:text-sm peer-placeholder-shown:text-gray-400 peer-focus:-top-2.5 peer-focus:text-xs peer-focus:text-primary-600"
      :class="hasValue ? '-top-2.5 text-xs text-gray-500' : '-top-2.5 text-xs text-gray-500'"
    >
      {{ label }}<span v-if="required" class="text-red-400 ml-0.5">*</span>
    </label>
  </div>
</template>
