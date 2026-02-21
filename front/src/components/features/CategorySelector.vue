<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import Dialog from '@/components/ui/Dialog.vue'
import DialogContent from '@/components/ui/DialogContent.vue'
import DialogHeader from '@/components/ui/DialogHeader.vue'
import DialogTitle from '@/components/ui/DialogTitle.vue'
import DialogFooter from '@/components/ui/DialogFooter.vue'
import Button from '@/components/ui/Button.vue'
import { useCategoriesStore } from '@/stores/categories'
import { useGroupsStore } from '@/stores/groups'
import type { Category } from '@/lib/api/schemas/category'
import type { Group } from '@/lib/api/schemas/group'
import { cn } from '@/lib/utils/cn'

const props = defineProps<{
  open: boolean
}>()

const emit = defineEmits<{
  (e: 'update:open', value: boolean): void
  (e: 'select', categoryId: string): void
}>()

const { t } = useI18n()
const categoriesStore = useCategoriesStore()
const groupsStore = useGroupsStore()

const selectedCategoryId = ref<string | null>(null)

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      selectedCategoryId.value = null
    }
  },
)

const groupedCategories = computed(() => {
  const groups = groupsStore.groups
  const categories = categoriesStore.categories

  const groupMap = new Map(groups.map((g) => [g.id, g]))
  const grouped = new Map<string, { group: Group; categories: Category[] }>()

  groups.forEach((g) => {
    grouped.set(g.id, { group: g, categories: [] })
  })

  categories.forEach((cat) => {
    const group = groupMap.get(cat.groupId)
    if (group) {
      const entry = grouped.get(group.id)
      if (entry) {
        entry.categories.push(cat)
      }
    }
  })

  return Array.from(grouped.values()).filter((g) => g.categories.length > 0)
})

const handleSelect = (categoryId: string) => {
  selectedCategoryId.value = categoryId
}

const handleConfirm = () => {
  if (selectedCategoryId.value) {
    emit('select', selectedCategoryId.value)
    emit('update:open', false)
  }
}

const handleCancel = () => {
  emit('update:open', false)
}
</script>

<template>
  <Dialog :open="open" @update:open="emit('update:open', $event)">
    <DialogContent class="sm:max-w-md max-h-[80vh] flex flex-col p-0 gap-0">
      <DialogHeader class="p-6 pb-2">
        <DialogTitle>{{ t('activities.timer.selectCategory') }}</DialogTitle>
      </DialogHeader>

      <div class="flex-1 overflow-y-auto p-6 pt-2">
        <div v-if="categoriesStore.categories.length === 0" class="text-center py-8 text-gray-500">
          {{ t('common.noData') }}
        </div>

        <div v-else class="space-y-6">
          <div v-for="section in groupedCategories" :key="section.group.id" class="space-y-3">
            <h3 class="text-sm font-medium text-gray-500 flex items-center gap-2">
              <span
                class="w-2 h-2 rounded-full"
                :style="{ backgroundColor: section.group.color || '#cbd5e1' }"
              ></span>
              {{ section.group.name }}
            </h3>

            <div class="grid grid-cols-1 gap-2">
              <button
                v-for="category in section.categories"
                :key="category.id"
                @click="handleSelect(category.id)"
                :class="
                  cn(
                    'flex items-center w-full text-left border rounded-lg p-3 transition-all',
                    selectedCategoryId === category.id
                      ? 'border-primary-500 bg-primary-50 ring-1 ring-primary-500'
                      : 'border-gray-200 hover:border-primary-300 hover:bg-gray-50',
                  )
                "
              >
                <span class="text-sm font-medium text-gray-900">{{ category.name }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <DialogFooter class="p-6 pt-2 border-t border-gray-100 mt-auto">
        <Button variant="outline" @click="handleCancel">
          {{ t('common.cancel') }}
        </Button>
        <Button :disabled="!selectedCategoryId" @click="handleConfirm">
          {{ t('activities.timer.startCategory') }}
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
