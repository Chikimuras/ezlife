<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { cn } from '@/lib/utils/cn'
import type { TaskList } from '@/lib/api/schemas/task'
import Button from '@/components/ui/Button.vue'
import { Plus, List, Edit2, Trash2 } from 'lucide-vue-next'

const { t } = useI18n()

defineProps<{
  taskLists: TaskList[]
  activeListId: string | null
}>()

const emit = defineEmits<{
  select: [id: string | null]
  create: []
  edit: [list: TaskList]
  delete: [list: TaskList]
}>()
</script>

<template>
  <div class="flex flex-col h-full bg-gray-50/50 border-r border-gray-200 w-64 p-4">
    <div class="flex items-center justify-between mb-4 px-2">
      <h2 class="text-sm font-semibold text-gray-500 uppercase tracking-wider">
        {{ t('tasks.taskLists') }}
      </h2>
      <Button variant="ghost" size="sm" class="h-6 w-6 p-0" @click="emit('create')">
        <Plus class="h-4 w-4" />
      </Button>
    </div>

    <div class="space-y-1 flex-1 overflow-y-auto">
      <!-- All Tasks -->
      <button
        @click="emit('select', null)"
        :class="cn(
          'w-full flex items-center justify-between px-3 py-2 text-sm font-medium rounded-md transition-colors group',
          activeListId === null
            ? 'bg-primary-50 text-primary-700'
            : 'text-gray-700 hover:bg-gray-100',
        )"
      >
        <div class="flex items-center">
          <List
            :class="cn(
              'w-4 h-4 mr-3',
              activeListId === null ? 'text-primary-600' : 'text-gray-400 group-hover:text-gray-500',
            )"
          />
          <span>{{ t('tasks.allTasks') }}</span>
        </div>
      </button>

      <!-- User Lists -->
      <div
        v-for="list in taskLists"
        :key="list.id"
        class="group relative flex items-center justify-between rounded-md px-3 py-2 text-sm font-medium transition-colors hover:bg-gray-100"
        :class="{ 'bg-primary-50 text-primary-700 hover:bg-primary-50': activeListId === list.id }"
      >
        <button
          @click="emit('select', list.id)"
          class="flex flex-1 items-center truncate"
        >
          <div
            class="mr-3 h-2.5 w-2.5 rounded-full"
            :style="{ backgroundColor: list.color || '#a855f7' }"
          ></div>
          <span class="truncate">{{ list.name }}</span>
        </button>

        <div class="flex items-center opacity-0 transition-opacity group-hover:opacity-100">
           <button
            @click.stop="emit('edit', list)"
            class="p-1 text-gray-400 hover:text-primary-600 rounded mr-1"
            :title="t('common.edit')"
          >
            <Edit2 class="h-3 w-3" />
          </button>
          <button
            @click.stop="emit('delete', list)"
            class="p-1 text-gray-400 hover:text-red-600 rounded"
            :title="t('common.delete')"
          >
            <Trash2 class="h-3 w-3" />
          </button>
        </div>
        
        <span
          v-if="activeListId !== list.id"
          class="ml-auto text-xs text-gray-400 group-hover:hidden"
        >
          {{ list.taskCount }}
        </span>
      </div>
      
      <div v-if="taskLists.length === 0" class="px-3 py-4 text-center">
        <p class="text-xs text-gray-500">{{ t('tasks.noLists') }}</p>
        <Button variant="ghost" size="sm" class="mt-1 h-auto p-0 text-primary-600 hover:text-primary-700 hover:bg-transparent" @click="emit('create')">
          {{ t('tasks.newList') }}
        </Button>
      </div>
    </div>

    <div class="mt-auto pt-4 border-t border-gray-200">
      <Button variant="outline" class="w-full justify-start" @click="emit('create')">
        <Plus class="mr-2 h-4 w-4" />
        {{ t('tasks.newList') }}
      </Button>
    </div>
  </div>
</template>
