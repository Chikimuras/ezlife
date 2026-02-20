<script setup lang="ts">
import { cn } from '@/lib/utils/cn'
import Select from '@/components/ui/Select.vue'
import SelectTrigger from '@/components/ui/SelectTrigger.vue'
import SelectValue from '@/components/ui/SelectValue.vue'
import SelectContent from '@/components/ui/SelectContent.vue'
import SelectItem from '@/components/ui/SelectItem.vue'

interface SelectOption {
  value: string
  label: string
}

interface Props {
  modelValue?: string
  label: string
  options: SelectOption[]
  placeholder?: string
  class?: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>

<template>
  <div :class="cn('relative', props.class)">
    <Select :model-value="modelValue" @update:model-value="emit('update:modelValue', $event)">
      <SelectTrigger>
        <SelectValue :placeholder="placeholder" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem
          v-for="opt in options"
          :key="opt.value"
          :value="opt.value"
        >
          {{ opt.label }}
        </SelectItem>
      </SelectContent>
    </Select>
    <label
      class="absolute left-3 -top-2.5 bg-white px-1 text-xs text-gray-500 pointer-events-none"
    >
      {{ label }}
    </label>
  </div>
</template>
