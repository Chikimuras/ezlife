<script setup lang="ts">
import { cn } from '@/lib/utils/cn'

interface Props {
  class?: string
}

const props = defineProps<Props>()
</script>

<template>
  <div :class="cn('flex flex-col space-y-2 mb-6', props.class)">
    <slot />
  </div>
</template>
