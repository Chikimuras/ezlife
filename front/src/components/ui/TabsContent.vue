<script setup lang="ts">
import { computed, inject, type Ref } from 'vue'
import { cn } from '@/lib/utils/cn'

interface Props {
  value: string
  class?: string
}

const props = defineProps<Props>()

const activeTab = inject<Ref<string>>('activeTab')

const isActive = computed(() => activeTab?.value === props.value)
</script>

<template>
  <div
    v-if="isActive"
    :class="
      cn(
        'mt-6 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500',
        props.class,
      )
    "
  >
    <slot />
  </div>
</template>
