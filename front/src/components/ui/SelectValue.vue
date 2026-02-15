<script setup lang="ts">
import { computed, inject, type Ref } from 'vue'

interface Props {
  placeholder?: string
}

const props = defineProps<Props>()

const selectedValue = inject<Ref<string>>('selectValue')

const displayValue = computed(() => selectedValue?.value || props.placeholder || 'Select...')
</script>

<template>
  <span>{{ displayValue }}</span>
</template>
