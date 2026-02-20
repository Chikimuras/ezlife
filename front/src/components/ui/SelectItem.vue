<script setup lang="ts">
import { computed, inject, onMounted, ref, type Ref } from 'vue'
import { cn } from '@/lib/utils/cn'

interface Props {
  value: string
  class?: string
}

const props = defineProps<Props>()

const selectedValue = inject<Ref<string>>('selectValue')
const selectItem = inject<(value: string, label?: string) => void>('selectItem')
const registerLabel = inject<(value: string, label: string) => void>('registerLabel')

const itemRef = ref<HTMLElement>()
const isSelected = computed(() => selectedValue?.value === props.value)

const getLabel = (): string => {
  return itemRef.value?.textContent?.trim() ?? props.value
}

onMounted(() => {
  if (registerLabel) {
    registerLabel(props.value, getLabel())
  }
})

const handleClick = () => {
  if (selectItem) {
    selectItem(props.value, getLabel())
  }
}
</script>

<template>
  <div
    ref="itemRef"
    :class="
      cn(
        'relative flex w-full cursor-pointer select-none items-center rounded-lg px-3 py-1.5 text-sm outline-none transition-colors hover:bg-primary-50 focus:bg-primary-50',
        isSelected ? 'bg-primary-50 text-primary-700 font-medium' : 'text-gray-900',
        props.class,
      )
    "
    @click="handleClick"
  >
    <span v-if="isSelected" class="absolute left-2 flex items-center justify-center">
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
        class="h-4 w-4 text-primary-600"
      >
        <path d="M20 6 9 17l-5-5" />
      </svg>
    </span>
    <span :class="isSelected ? 'ml-6' : ''">
      <slot />
    </span>
  </div>
</template>
