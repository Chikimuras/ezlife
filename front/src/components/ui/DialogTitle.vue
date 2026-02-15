<script setup lang="ts">
import { cn } from '@/lib/utils/cn'

interface Props {
  class?: string
}

const props = defineProps<Props>()
</script>

<template>
  <h2 :class="cn('text-2xl font-bold text-gray-900', props.class)">
    <slot />
  </h2>
</template>
