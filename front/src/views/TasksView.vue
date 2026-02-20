<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import AuthenticatedLayout from '@/components/layouts/AuthenticatedLayout.vue'
import TaskListSidebar from '@/components/features/TaskListSidebar.vue'
import TaskCard from '@/components/features/TaskCard.vue'
import TaskDialog from '@/components/features/TaskDialog.vue'
import TaskToActivityDialog from '@/components/features/TaskToActivityDialog.vue'
import { useTasksStore } from '@/stores/tasks'
import { useCategoriesStore } from '@/stores/categories'
import { useGroupsStore } from '@/stores/groups'
import { useActivitiesStore } from '@/stores/activities'
import type { Task, TaskList, CreateTaskList } from '@/lib/api/schemas/task'
import Button from '@/components/ui/Button.vue'
import Dialog from '@/components/ui/Dialog.vue'
import DialogContent from '@/components/ui/DialogContent.vue'
import DialogHeader from '@/components/ui/DialogHeader.vue'
import DialogTitle from '@/components/ui/DialogTitle.vue'
import DialogFooter from '@/components/ui/DialogFooter.vue'
import FloatingInput from '@/components/ui/FloatingInput.vue'
import Label from '@/components/ui/Label.vue'
import { Plus, Pipette, Calendar, CalendarDays, LayoutGrid } from 'lucide-vue-next'
import type { TaskView } from '@/stores/tasks'

const { t } = useI18n()
const tasksStore = useTasksStore()
const categoriesStore = useCategoriesStore()
const groupsStore = useGroupsStore()
const activitiesStore = useActivitiesStore()

// State
const isTaskDialogOpen = ref(false)
const isListDialogOpen = ref(false)
const isConvertDialogOpen = ref(false)
const isCompleteConfirmOpen = ref(false)
const selectedTask = ref<Task | undefined>(undefined)
const taskToComplete = ref<Task | undefined>(undefined)
const selectedList = ref<TaskList | undefined>(undefined)

// List Form State
const listFormData = ref<CreateTaskList>({
  name: '',
  color: '#a855f7',
  icon: undefined,
  position: 0,
})
const showCustomPicker = ref(false)

// 6 columns × 3 rows — each column is one color family (light → dark)
const colorGrid = [
  ['#DBEAFE', '#D1FAE5', '#FEE2E2', '#EDE9FE', '#FEF9C3', '#F3F4F6'],
  ['#93C5FD', '#6EE7B7', '#FCA5A5', '#C4B5FD', '#FDE68A', '#D1D5DB'],
  ['#3B82F6', '#10B981', '#EF4444', '#8B5CF6', '#F59E0B', '#6B7280'],
]

onMounted(async () => {
  await Promise.all([
    tasksStore.fetchTaskLists(),
    tasksStore.fetchTasks(),
    categoriesStore.fetchCategories(),
    groupsStore.fetchGroups(),
  ])
})

// Computed
const currentListName = computed(() => {
  if (!tasksStore.activeListId) return t('tasks.allTasks')
  return tasksStore.activeList?.name || t('tasks.taskLists')
})

const todoTasks = computed(() => tasksStore.todoTasks)
const inProgressTasks = computed(() => tasksStore.inProgressTasks)
const doneTasks = computed(() => tasksStore.doneTasks)

// Methods - Lists
const handleSelectList = (id: string | null) => {
  tasksStore.setActiveList(id)
}

const handleCreateList = () => {
  selectedList.value = undefined
  listFormData.value = { name: '', color: '#a855f7', position: tasksStore.taskLists.length }
  isListDialogOpen.value = true
}

const handleEditList = (list: TaskList) => {
  selectedList.value = list
  listFormData.value = {
    name: list.name,
    color: list.color || '#a855f7',
    icon: list.icon || undefined,
    position: list.position,
  }
  isListDialogOpen.value = true
}

const handleDeleteList = async (list: TaskList) => {
  if (confirm(t('tasks.confirmDeleteList'))) {
    await tasksStore.deleteTaskList(list.id)
  }
}

const handleSaveList = async () => {
  try {
    if (selectedList.value) {
      await tasksStore.updateTaskList(selectedList.value.id, listFormData.value)
    } else {
      await tasksStore.createTaskList(listFormData.value)
    }
    isListDialogOpen.value = false
  } catch (error) {
    console.error(error)
  }
}

// Methods - Tasks
const handleCreateTask = () => {
  selectedTask.value = undefined
  isTaskDialogOpen.value = true
}

const handleEditTask = (task: Task) => {
  selectedTask.value = task
  isTaskDialogOpen.value = true
}

const handleDeleteTask = async (task: Task) => {
  if (confirm(t('tasks.confirmDelete'))) {
    await tasksStore.deleteTask(task.id)
  }
}

const handleCompleteTask = async (task: Task) => {
  try {
    if (task.status === 'done') {
      await tasksStore.updateTask(task.id, { status: 'todo' })
    } else {
      taskToComplete.value = task
      isCompleteConfirmOpen.value = true
    }
  } catch (error) {
    console.error(error)
  }
}

const handleStatusChange = async (task: Task, status: string) => {
  try {
    // If undoing from 'done' to 'todo', delete linked activities first
    if (task.status === 'done' && status === 'todo' && task.activityIds && task.activityIds.length > 0) {
      await Promise.all(task.activityIds.map(id => activitiesStore.deleteActivity(id)))
    }
    await tasksStore.updateTask(task.id, { status: status as 'todo' | 'in_progress' | 'done' })
  } catch (error) {
    console.error(error)
  }
}

const handleConfirmComplete = async (addToTracker: boolean) => {
  if (!taskToComplete.value) return

  try {
    if (addToTracker) {
      isCompleteConfirmOpen.value = false
      selectedTask.value = taskToComplete.value
      isConvertDialogOpen.value = true
    } else {
      await tasksStore.completeTask(taskToComplete.value.id, { addToTracker: false })
      isCompleteConfirmOpen.value = false
      taskToComplete.value = undefined
    }
  } catch (error) {
    console.error(error)
  }
}

const handleConvertToActivity = (task: Task) => {
  selectedTask.value = task
  isConvertDialogOpen.value = true
}

const handleTaskSaved = () => {
  tasksStore.fetchTasks() // Refresh tasks
}

const handleConvertSaved = () => {
  tasksStore.fetchTasks() // Refresh tasks to see updated status/link
}

const handleViewChange = (view: TaskView) => {
  tasksStore.setActiveView(view)
}
</script>

<template>
  <AuthenticatedLayout>
    <div class="flex h-[calc(100vh-64px)] overflow-hidden">
      <!-- Sidebar -->
      <TaskListSidebar
        :task-lists="tasksStore.taskLists"
        :active-list-id="tasksStore.activeListId"
        @select="handleSelectList"
        @create="handleCreateList"
        @edit="handleEditList"
        @delete="handleDeleteList"
      />

      <!-- Main Content -->
      <div class="flex-1 flex flex-col min-w-0 bg-white">
        <!-- Header -->
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <h1 class="text-xl font-semibold text-gray-900 truncate">{{ currentListName }}</h1>
          <div class="flex items-center gap-3">
            <!-- View Selector -->
            <div class="flex items-center bg-gray-100 rounded-lg p-1">
              <button
                @click="handleViewChange('today')"
                :class="[
                  'flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-md transition-colors',
                  tasksStore.activeView === 'today'
                    ? 'bg-white text-primary-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                ]"
              >
                <Calendar class="h-4 w-4" />
                {{ t('tasks.views.today') }}
              </button>
              <button
                @click="handleViewChange('week')"
                :class="[
                  'flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-md transition-colors',
                  tasksStore.activeView === 'week'
                    ? 'bg-white text-primary-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                ]"
              >
                <CalendarDays class="h-4 w-4" />
                {{ t('tasks.views.week') }}
              </button>
              <button
                @click="handleViewChange('all')"
                :class="[
                  'flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-md transition-colors',
                  tasksStore.activeView === 'all'
                    ? 'bg-white text-primary-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                ]"
              >
                <LayoutGrid class="h-4 w-4" />
                {{ t('tasks.views.all') }}
              </button>
            </div>
            <Button @click="handleCreateTask">
              <Plus class="mr-2 h-4 w-4" />
              {{ t('tasks.newTask') }}
            </Button>
          </div>
        </div>

        <!-- Task Columns -->
        <div class="flex-1 overflow-y-auto p-6">
          <div v-if="tasksStore.loading && tasksStore.tasks.length === 0" class="flex justify-center py-12">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>

          <div v-else-if="tasksStore.filteredTasks.length === 0" class="flex flex-col items-center justify-center h-full text-center text-gray-500">
            <p class="mb-2 text-lg font-medium">{{ t('tasks.noTasks') }}</p>
            <p class="text-sm mb-4">{{ t('tasks.noTasksDescription') }}</p>
            <Button variant="outline" @click="handleCreateTask">{{ t('tasks.newTask') }}</Button>
          </div>

          <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full">
            <!-- Todo -->
            <div class="flex flex-col gap-4">
              <h3 class="font-medium text-gray-500 flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-gray-300"></span>
                {{ t('tasks.statuses.todo') }}
                <span class="ml-auto text-xs bg-gray-100 px-2 py-0.5 rounded-full">{{ todoTasks.length }}</span>
              </h3>
              <TransitionGroup name="task-list" tag="div" class="flex flex-col gap-3">
                <TaskCard
                  v-for="task in todoTasks"
                  :key="task.id"
                  :task="task"
                  @complete="handleCompleteTask"
                  @edit="handleEditTask"
                  @delete="handleDeleteTask"
                  @convert-to-activity="handleConvertToActivity"
                  @status-change="handleStatusChange"
                />
              </TransitionGroup>
            </div>

            <!-- In Progress -->
            <div class="flex flex-col gap-4">
              <h3 class="font-medium text-blue-500 flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-blue-300"></span>
                {{ t('tasks.statuses.in_progress') }}
                <span class="ml-auto text-xs bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full">{{ inProgressTasks.length }}</span>
              </h3>
              <TransitionGroup name="task-list" tag="div" class="flex flex-col gap-3">
                <TaskCard
                  v-for="task in inProgressTasks"
                  :key="task.id"
                  :task="task"
                  @complete="handleCompleteTask"
                  @edit="handleEditTask"
                  @delete="handleDeleteTask"
                  @convert-to-activity="handleConvertToActivity"
                  @status-change="handleStatusChange"
                />
              </TransitionGroup>
            </div>

            <!-- Done -->
            <div class="flex flex-col gap-4">
              <h3 class="font-medium text-green-500 flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-green-300"></span>
                {{ t('tasks.statuses.done') }}
                <span class="ml-auto text-xs bg-green-50 text-green-600 px-2 py-0.5 rounded-full">{{ doneTasks.length }}</span>
              </h3>
              <TransitionGroup name="task-list" tag="div" class="flex flex-col gap-3 opacity-75">
                <TaskCard
                  v-for="task in doneTasks"
                  :key="task.id"
                  :task="task"
                  @complete="handleCompleteTask"
                  @edit="handleEditTask"
                  @delete="handleDeleteTask"
                  @convert-to-activity="handleConvertToActivity"
                  @status-change="handleStatusChange"
                />
              </TransitionGroup>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Task Dialog -->
    <TaskDialog
      v-model:open="isTaskDialogOpen"
      :task="selectedTask"
      :task-list-id="tasksStore.activeListId || tasksStore.taskLists[0]?.id || ''"
      @saved="handleTaskSaved"
    />

    <!-- Convert Dialog -->
    <TaskToActivityDialog
      v-if="selectedTask"
      v-model:open="isConvertDialogOpen"
      :task="selectedTask"
      @saved="handleConvertSaved"
    />

    <!-- List Dialog -->
    <Dialog v-model:open="isListDialogOpen">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{{ selectedList ? t('tasks.editList') : t('tasks.newList') }}</DialogTitle>
        </DialogHeader>
        <div class="grid gap-4 py-4">
          <FloatingInput
            v-model="listFormData.name"
            :label="t('tasks.listName')"
            required
          />
          <div class="grid gap-2">
            <Label>{{ t('tasks.color') }}</Label>
            <div class="flex items-end gap-3">
              <div class="grid grid-cols-6 gap-x-3 gap-y-1.5">
                <template v-for="(row, rowIdx) in colorGrid" :key="rowIdx">
                  <button
                    v-for="color in row"
                    :key="color"
                    type="button"
                    class="w-7 h-7 rounded-full border-2 transition-all hover:scale-110"
                    :class="listFormData.color === color ? 'border-gray-900 ring-2 ring-primary-300 scale-110' : 'border-transparent'"
                    :style="{ backgroundColor: color }"
                    @click="listFormData.color = color"
                  />
                </template>
              </div>
              <div class="relative">
                <button
                  type="button"
                  class="w-7 h-7 rounded-full border-2 border-dashed border-gray-300 flex items-center justify-center text-gray-400 hover:border-primary-400 hover:text-primary-500 transition-all"
                  @click="showCustomPicker = !showCustomPicker"
                >
                  <Pipette class="w-3.5 h-3.5" />
                </button>
                <div
                  v-if="showCustomPicker"
                  class="absolute bottom-9 left-0 z-10 bg-white rounded-lg shadow-lg border border-gray-200 p-3 flex flex-col gap-2"
                >
                  <input
                    type="color"
                    :value="listFormData.color"
                    @input="listFormData.color = ($event.target as HTMLInputElement).value"
                    class="w-32 h-32 rounded-lg cursor-pointer border-0 p-0"
                  />
                  <span class="text-xs text-center text-gray-500 font-mono">{{ listFormData.color }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" @click="isListDialogOpen = false">{{ t('common.cancel') }}</Button>
          <Button @click="handleSaveList" :disabled="!listFormData.name">{{ t('common.save') }}</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
    <Dialog v-model:open="isCompleteConfirmOpen">
      <DialogContent class="sm:max-w-[400px]">
        <DialogHeader>
          <DialogTitle>{{ t('tasks.completeDialog.title') }}</DialogTitle>
        </DialogHeader>
        <p class="text-sm text-gray-600 py-4">{{ t('tasks.completeDialog.addToTrackerQuestion') }}</p>
        <DialogFooter>
          <Button variant="outline" @click="handleConfirmComplete(false)">{{ t('common.no') }}</Button>
          <Button @click="handleConfirmComplete(true)">{{ t('tasks.addToTracker') }}</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </AuthenticatedLayout>
</template>

<style>
.task-list-move,
.task-list-enter-active,
.task-list-leave-active {
  transition: all 0.3s ease;
}
.task-list-enter-from,
.task-list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
.task-list-leave-active {
  position: absolute;
}
</style>
