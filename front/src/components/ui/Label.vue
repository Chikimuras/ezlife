<script setup lang="ts">
import { computed } from 'vue'
import { cn } from '@/lib/utils/cn'

interface Props {
  for?: string
  class?: string
}

const props = defineProps<Props>()

const labelClass = computed(() => cn('block text-sm font-medium text-gray-700 mb-2', props.class))
</script>

<template>
  <label :for="for" :class="labelClass">
    <slot />
  </label>
</template>
