<script setup lang="ts">
import { inject, type Ref } from 'vue'

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const dialogOpen = inject<Ref<boolean>>('dialogOpen')

const handleClick = (event: MouseEvent) => {
  if (dialogOpen) {
    dialogOpen.value = true
  }
  emit('click', event)
}
</script>

<template>
  <div @click="handleClick">
    <slot />
  </div>
</template>
