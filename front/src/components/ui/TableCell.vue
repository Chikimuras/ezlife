<script setup lang="ts">
import { cn } from '@/lib/utils/cn'

interface Props {
  class?: string
}

const props = defineProps<Props>()
</script>

<template>
  <td :class="cn('px-3 py-3 text-sm text-gray-900', props.class)">
    <slot />
  </td>
</template>
