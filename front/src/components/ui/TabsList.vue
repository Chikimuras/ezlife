<script setup lang="ts">
import { cn } from '@/lib/utils/cn'

interface Props {
  class?: string
}

const props = defineProps<Props>()
</script>

<template>
  <div
    :class="cn('inline-flex items-center justify-center rounded-xl bg-gray-100 p-1.5', props.class)"
  >
    <slot />
  </div>
</template>
