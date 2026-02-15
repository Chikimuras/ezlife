<script setup lang="ts">
import { inject, type Ref } from 'vue'
import { cn } from '@/lib/utils/cn'

interface Props {
  class?: string
}

const props = defineProps<Props>()

const isOpen = inject<Ref<boolean>>('selectOpen')

const toggleOpen = () => {
  if (isOpen) {
    isOpen.value = !isOpen.value
  }
}
</script>

<template>
  <button
    type="button"
    :class="
      cn(
        'flex w-full items-center justify-between px-3 py-2 border border-gray-200 rounded-lg bg-white text-gray-900 placeholder:text-gray-500 focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all disabled:cursor-not-allowed disabled:opacity-50',
        props.class,
      )
    "
    @click="toggleOpen"
  >
    <slot />
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
      class="h-4 w-4 text-gray-500"
    >
      <path d="m6 9 6 6 6-6" />
    </svg>
  </button>
</template>
