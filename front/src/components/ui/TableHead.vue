<script setup lang="ts">
import { cn } from '@/lib/utils/cn'

interface Props {
  class?: string
}

const props = defineProps<Props>()
</script>

<template>
  <th
    :class="
      cn(
        'px-3 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wide',
        props.class,
      )
    "
  >
    <slot />
  </th>
</template>
