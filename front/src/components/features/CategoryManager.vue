<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useCategoriesStore } from '@/stores/categories'
import { useGroupsStore } from '@/stores/groups'
import { useI18n } from 'vue-i18n'
import { useToast } from '@/composables/useToast'
import Table from '@/components/ui/Table.vue'
import TableBody from '@/components/ui/TableBody.vue'
import TableCell from '@/components/ui/TableCell.vue'
import TableHead from '@/components/ui/TableHead.vue'
import TableHeader from '@/components/ui/TableHeader.vue'
import TableRow from '@/components/ui/TableRow.vue'
import Button from '@/components/ui/Button.vue'
import Dialog from '@/components/ui/Dialog.vue'
import DialogContent from '@/components/ui/DialogContent.vue'
import DialogHeader from '@/components/ui/DialogHeader.vue'
import DialogTitle from '@/components/ui/DialogTitle.vue'
import DialogFooter from '@/components/ui/DialogFooter.vue'
import DialogTrigger from '@/components/ui/DialogTrigger.vue'
import FloatingInput from '@/components/ui/FloatingInput.vue'
import FloatingSelect from '@/components/ui/FloatingSelect.vue'
import Checkbox from '@/components/ui/Checkbox.vue'
import Label from '@/components/ui/Label.vue'
import type { CreateCategory } from '@/lib/api/schemas/category'

const { t } = useI18n()
const { success, error } = useToast()
const categoriesStore = useCategoriesStore()
const groupsStore = useGroupsStore()

const isAddDialogOpen = ref(false)
const isEditDialogOpen = ref(false)
const isDeleteDialogOpen = ref(false)
const editingCategoryId = ref<string | null>(null)
const deletingCategoryId = ref<string | null>(null)

const formData = ref<CreateCategory>({
  name: '',
  groupId: '',
  priority: 1,
  minWeeklyHours: 0,
  targetWeeklyHours: 0,
  maxWeeklyHours: 0,
  unit: 'hours',
  mandatory: false,
})

onMounted(async () => {
  await Promise.all([categoriesStore.fetchCategories(), groupsStore.fetchGroups()])
})

const getGroupName = (groupId: string) => {
  return groupsStore.groups.find((g) => g.id === groupId)?.name ?? '-'
}

const getGroupColor = (groupId: string) => {
  return groupsStore.groups.find((g) => g.id === groupId)?.color
}

const resetForm = () => {
  formData.value = {
    name: '',
    groupId: '',
    priority: 1,
    minWeeklyHours: 0,
    targetWeeklyHours: 0,
    maxWeeklyHours: 0,
    unit: 'hours',
    mandatory: false,
  }
}

const handleAdd = async () => {
  try {
    await categoriesStore.createCategory(formData.value)
    isAddDialogOpen.value = false
    resetForm()
    success(t('settings.categories.messages.created'))
  } catch (err) {
    error(t('settings.categories.messages.createError'))
  }
}

const openEditDialog = (categoryId: string) => {
  const category = categoriesStore.categories.find((c) => c.id === categoryId)
  if (category) {
    editingCategoryId.value = categoryId
    formData.value = {
      name: category.name,
      groupId: category.groupId,
      priority: category.priority,
      minWeeklyHours: category.minWeeklyHours,
      targetWeeklyHours: category.targetWeeklyHours,
      maxWeeklyHours: category.maxWeeklyHours,
      unit: category.unit,
      mandatory: category.mandatory,
    }
    isEditDialogOpen.value = true
  }
}

const handleEdit = async () => {
  if (editingCategoryId.value) {
    try {
      await categoriesStore.updateCategory(editingCategoryId.value, formData.value)
      isEditDialogOpen.value = false
      resetForm()
      editingCategoryId.value = null
      success(t('settings.categories.messages.updated'))
    } catch (err) {
      error(t('settings.categories.messages.updateError'))
    }
  }
}

const openDeleteDialog = (categoryId: string) => {
  deletingCategoryId.value = categoryId
  isDeleteDialogOpen.value = true
}

const handleDelete = async () => {
  if (deletingCategoryId.value) {
    try {
      await categoriesStore.deleteCategory(deletingCategoryId.value)
      isDeleteDialogOpen.value = false
      deletingCategoryId.value = null
      success(t('settings.categories.messages.deleted'))
    } catch (err) {
      error(t('settings.categories.messages.deleteError'))
    }
  }
}
</script>

<template>
  <div class="space-y-3">
    <div class="flex justify-between items-center">
      <h2 class="text-base font-semibold">{{ t('settings.categories.title') }}</h2>

      <Dialog v-model:open="isAddDialogOpen">
        <DialogTrigger as-child>
          <Button @click="resetForm">{{ t('settings.categories.add') }}</Button>
        </DialogTrigger>
        <DialogContent class="max-w-2xl">
          <DialogHeader>
            <DialogTitle>{{ t('settings.categories.add') }}</DialogTitle>
          </DialogHeader>

          <div class="grid gap-3 py-3">
            <div class="grid gap-1.5">
              <FloatingInput v-model="formData.name" :label="t('settings.categories.fields.name')" />
            </div>

            <div class="grid gap-1.5">
              <FloatingSelect
                v-model="formData.groupId"
                :label="t('settings.categories.fields.group')"
                :options="groupsStore.groups.map((g) => ({ value: g.id, label: g.name }))"
              />
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div class="grid gap-1.5">
                <FloatingInput
                  v-model.number="formData.priority"
                  :label="t('settings.categories.fields.priority')"
                  type="number"
                  min="1"
                />
              </div>

              <div class="grid gap-1.5">
                <FloatingSelect
                  v-model="formData.unit"
                  :label="t('settings.categories.fields.unit')"
                  :options="[
                    { value: 'hours', label: t('settings.categories.units.hours') },
                    { value: 'minutes', label: t('settings.categories.units.minutes') },
                    { value: 'count', label: t('settings.categories.units.count') },
                  ]"
                />
              </div>
            </div>

            <div class="grid grid-cols-3 gap-3">
              <div class="grid gap-1.5">
                <FloatingInput
                  v-model.number="formData.minWeeklyHours"
                  :label="t('settings.categories.fields.minWeekly')"
                  type="number"
                  min="0"
                />
              </div>

              <div class="grid gap-2">
                <FloatingInput
                  v-model.number="formData.targetWeeklyHours"
                  :label="t('settings.categories.fields.targetWeekly')"
                  type="number"
                  min="0"
                />
              </div>

              <div class="grid gap-2">
                <FloatingInput
                  v-model.number="formData.maxWeeklyHours"
                  :label="t('settings.categories.fields.maxWeekly')"
                  type="number"
                  min="0"
                />
              </div>
            </div>

            <div class="flex items-center gap-2">
              <Checkbox id="mandatory" v-model:checked="formData.mandatory" />
              <Label for="mandatory" class="cursor-pointer">{{
                t('settings.categories.fields.mandatory')
              }}</Label>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" @click="isAddDialogOpen = false">{{
              t('common.cancel')
            }}</Button>
            <Button @click="handleAdd">{{ t('common.save') }}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>

    <div v-if="categoriesStore.loading" class="text-center py-4">
      {{ t('common.loading') }}
    </div>

    <div v-else-if="categoriesStore.error" class="text-red-500 py-4">
      {{ categoriesStore.error }}
      <Button @click="categoriesStore.fetchCategories()" variant="outline" class="ml-4">
        {{ t('common.retry') }}
      </Button>
    </div>

    <div v-else-if="categoriesStore.categories.length === 0" class="text-center py-12 space-y-4">
      <div class="text-gray-400 text-6xl">📋</div>
      <h3 class="text-sm font-semibold text-gray-700">No categories yet</h3>
      <p class="text-gray-500">Get started by creating your first activity category</p>
      <Button @click="isAddDialogOpen = true">{{ t('settings.categories.add') }}</Button>
    </div>

    <div v-else>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>{{ t('settings.categories.fields.name') }}</TableHead>
            <TableHead>{{ t('settings.categories.fields.group') }}</TableHead>
            <TableHead>{{ t('settings.categories.fields.priority') }}</TableHead>
            <TableHead>{{ t('settings.categories.fields.minWeekly') }}</TableHead>
            <TableHead>{{ t('settings.categories.fields.targetWeekly') }}</TableHead>
            <TableHead>{{ t('settings.categories.fields.maxWeekly') }}</TableHead>
            <TableHead>{{ t('settings.categories.fields.unit') }}</TableHead>
            <TableHead>{{ t('settings.categories.fields.mandatory') }}</TableHead>
            <TableHead class="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow v-for="category in categoriesStore.categories" :key="category.id">
            <TableCell class="font-medium">{{ category.name }}</TableCell>
            <TableCell>
              <span
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold"
                :style="{ backgroundColor: getGroupColor(category.groupId), color: 'white' }"
              >
                {{ getGroupName(category.groupId) }}
              </span>
            </TableCell>
            <TableCell>{{ category.priority }}</TableCell>
            <TableCell>{{ category.minWeeklyHours }}</TableCell>
            <TableCell>{{ category.targetWeeklyHours }}</TableCell>
            <TableCell>{{ category.maxWeeklyHours }}</TableCell>
            <TableCell>{{ t(`settings.categories.units.${category.unit}`) }}</TableCell>
            <TableCell>{{ category.mandatory ? t('common.yes') : t('common.no') }}</TableCell>
            <TableCell class="text-right space-x-2">
              <Button variant="ghost" size="sm" @click="openEditDialog(category.id)">
                {{ t('common.edit') }}
              </Button>
              <Button variant="ghost" size="sm" @click="openDeleteDialog(category.id)">
                {{ t('common.delete') }}
              </Button>
            </TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </div>

    <Dialog v-model:open="isEditDialogOpen">
      <DialogContent class="max-w-2xl">
        <DialogHeader>
          <DialogTitle>{{ t('settings.categories.edit') }}</DialogTitle>
        </DialogHeader>

        <div class="grid gap-4 py-4">
          <div class="grid gap-2">
            <FloatingInput v-model="formData.name" :label="t('settings.categories.fields.name')" />
          </div>

          <div class="grid gap-2">
            <FloatingSelect
              v-model="formData.groupId"
              :label="t('settings.categories.fields.group')"
              :options="groupsStore.groups.map((g) => ({ value: g.id, label: g.name }))"
            />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div class="grid gap-2">
              <FloatingInput
                v-model.number="formData.priority"
                :label="t('settings.categories.fields.priority')"
                type="number"
                min="1"
              />
            </div>

            <div class="grid gap-2">
              <FloatingSelect
                v-model="formData.unit"
                :label="t('settings.categories.fields.unit')"
                :options="[
                  { value: 'hours', label: t('settings.categories.units.hours') },
                  { value: 'minutes', label: t('settings.categories.units.minutes') },
                  { value: 'count', label: t('settings.categories.units.count') },
                ]"
              />
            </div>
          </div>

          <div class="grid grid-cols-3 gap-4">
            <div class="grid gap-2">
              <FloatingInput
                v-model.number="formData.minWeeklyHours"
                :label="t('settings.categories.fields.minWeekly')"
                type="number"
                min="0"
              />
            </div>

            <div class="grid gap-2">
              <FloatingInput
                v-model.number="formData.targetWeeklyHours"
                :label="t('settings.categories.fields.targetWeekly')"
                type="number"
                min="0"
              />
            </div>

            <div class="grid gap-2">
              <FloatingInput
                v-model.number="formData.maxWeeklyHours"
                :label="t('settings.categories.fields.maxWeekly')"
                type="number"
                min="0"
              />
            </div>
          </div>

          <div class="flex items-center gap-2">
            <Checkbox id="edit-mandatory" v-model:checked="formData.mandatory" />
            <Label for="edit-mandatory" class="cursor-pointer">{{
              t('settings.categories.fields.mandatory')
            }}</Label>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" @click="isEditDialogOpen = false">{{
            t('common.cancel')
          }}</Button>
          <Button @click="handleEdit">{{ t('common.save') }}</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    <Dialog v-model:open="isDeleteDialogOpen">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{{ t('settings.categories.delete') }}</DialogTitle>
        </DialogHeader>
        <p>{{ t('settings.categories.confirmDelete') }}</p>
        <DialogFooter>
          <Button variant="outline" @click="isDeleteDialogOpen = false">{{
            t('common.cancel')
          }}</Button>
          <Button variant="destructive" @click="handleDelete">{{ t('common.delete') }}</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
</template>
