<script setup lang="ts">
import { cn } from '@/lib/utils/cn'

interface Props {
  class?: string
}

const props = defineProps<Props>()
</script>

<template>
  <tbody :class="cn('[&_tr:nth-child(even)]:bg-primary-50', props.class)">
    <slot />
  </tbody>
</template>
