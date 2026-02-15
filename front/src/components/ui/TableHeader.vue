<script setup lang="ts">
import { cn } from '@/lib/utils/cn'

interface Props {
  class?: string
}

const props = defineProps<Props>()
</script>

<template>
  <thead :class="cn('', props.class)">
    <slot />
  </thead>
</template>
