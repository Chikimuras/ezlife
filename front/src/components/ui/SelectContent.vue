<script setup lang="ts">
import { inject, type Ref, computed } from 'vue'
import { cn } from '@/lib/utils/cn'

interface Props {
  class?: string
}

const props = defineProps<Props>()

const isOpen = inject<Ref<boolean>>('selectOpen')
const isSelectOpen = computed(() => isOpen?.value === true)
</script>

<template>
  <div
    v-if="isSelectOpen"
    :class="
      cn(
        'absolute z-50 mt-2 max-h-96 w-full overflow-auto rounded-xl border border-gray-100 bg-white shadow-xl',
        props.class,
      )
    "
  >
    <div class="p-1.5">
      <slot />
    </div>
  </div>
</template>
