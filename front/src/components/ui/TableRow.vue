<script setup lang="ts">
import { cn } from '@/lib/utils/cn'

interface Props {
  class?: string
}

const props = defineProps<Props>()
</script>

<template>
  <tr :class="cn('hover:bg-gray-50/50 transition-colors', props.class)">
    <slot />
  </tr>
</template>
