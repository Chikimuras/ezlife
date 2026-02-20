<script setup lang="ts">
import { onMounted, ref } from 'vue'
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
import Badge from '@/components/ui/Badge.vue'
import type { CreateGroup } from '@/lib/api/schemas/group'

const { t } = useI18n()
const { success, error } = useToast()
const groupsStore = useGroupsStore()

const isAddDialogOpen = ref(false)
const isEditDialogOpen = ref(false)
const isDeleteDialogOpen = ref(false)
const editingGroupId = ref<string | null>(null)
const deletingGroupId = ref<string | null>(null)

const formData = ref<CreateGroup>({
  name: '',
  color: '#8B5CF6',
})

// Calculate contrasting text color based on background luminance
const getContrastTextColor = (hexColor: string): string => {
  // Remove # if present
  const hex = hexColor.replace('#', '')

  // Convert to RGB
  const r = parseInt(hex.substring(0, 2), 16)
  const g = parseInt(hex.substring(2, 4), 16)
  const b = parseInt(hex.substring(4, 6), 16)

  // Calculate relative luminance (WCAG formula)
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255

  // Return dark text for light colors, light text for dark colors
  return luminance > 0.5 ? '#1c1917' : '#fafaf9' // gray-900 : gray-50
}

onMounted(async () => {
  await groupsStore.fetchGroups()
})

const resetForm = () => {
  formData.value = {
    name: '',
    color: '#8B5CF6',
  }
}

const handleAdd = async () => {
  try {
    await groupsStore.createGroup(formData.value)
    isAddDialogOpen.value = false
    resetForm()
    success(t('settings.groups.messages.created'))
  } catch (err) {
    error(t('settings.groups.messages.createError'))
  }
}

const openEditDialog = (groupId: string) => {
  const group = groupsStore.groups.find((g) => g.id === groupId)
  if (group) {
    editingGroupId.value = groupId
    formData.value = {
      name: group.name,
      color: group.color ?? '#8B5CF6',
    }
    isEditDialogOpen.value = true
  }
}

const handleEdit = async () => {
  if (editingGroupId.value) {
    try {
      await groupsStore.updateGroup(editingGroupId.value, formData.value)
      isEditDialogOpen.value = false
      resetForm()
      editingGroupId.value = null
      success(t('settings.groups.messages.updated'))
    } catch (err) {
      error(t('settings.groups.messages.updateError'))
    }
  }
}

const openDeleteDialog = (groupId: string) => {
  deletingGroupId.value = groupId
  isDeleteDialogOpen.value = true
}

const handleDelete = async () => {
  if (deletingGroupId.value) {
    try {
      await groupsStore.deleteGroup(deletingGroupId.value)
      isDeleteDialogOpen.value = false
      deletingGroupId.value = null
      success(t('settings.groups.messages.deleted'))
    } catch (err) {
      error(t('settings.groups.messages.deleteError'))
    }
  }
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex justify-between items-center">
      <h2 class="text-sm font-semibold">{{ t('settings.groups.title') }}</h2>

      <Dialog v-model:open="isAddDialogOpen">
        <DialogTrigger as-child>
          <Button @click="resetForm">{{ t('settings.groups.add') }}</Button>
        </DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{{ t('settings.groups.add') }}</DialogTitle>
          </DialogHeader>

          <div class="grid gap-4 py-4">
            <div class="grid gap-1.5">
              <FloatingInput v-model="formData.name" :label="t('settings.groups.fields.name')" />
            </div>

            <div class="grid gap-1.5">
              <label class="text-xs text-gray-500 font-medium ml-1">{{
                t('settings.groups.fields.color')
              }}</label>
              <div class="flex items-center gap-2">
                <input
                  type="color"
                  v-model="formData.color"
                  class="w-10 h-10 rounded-lg cursor-pointer border border-gray-200 p-0.5"
                />
                <FloatingInput v-model="formData.color" label="Hex" class="flex-1" />
              </div>
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

    <div v-if="groupsStore.loading" class="text-center py-4">
      {{ t('common.loading') }}
    </div>

    <div v-else-if="groupsStore.error" class="text-red-500 py-4">
      {{ groupsStore.error }}
      <Button @click="groupsStore.fetchGroups()" variant="outline" class="ml-4">
        {{ t('common.retry') }}
      </Button>
    </div>

    <div v-else-if="groupsStore.groups.length === 0" class="text-center py-12 space-y-4">
      <div class="text-gray-400 text-6xl">🏷️</div>
      <h3 class="text-sm font-semibold text-gray-700">No groups yet</h3>
      <p class="text-gray-500">Create groups to organize your activity categories</p>
      <Button @click="isAddDialogOpen = true">{{ t('settings.groups.add') }}</Button>
    </div>

    <div v-else>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>{{ t('settings.groups.fields.name') }}</TableHead>
            <TableHead>{{ t('settings.groups.fields.color') }}</TableHead>
            <TableHead class="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow v-for="group in groupsStore.groups" :key="group.id">
            <TableCell class="font-medium">{{ group.name }}</TableCell>
            <TableCell>
              <Badge
                :style="{
                  backgroundColor: group.color,
                  color: getContrastTextColor(group.color ?? '#8B5CF6'),
                }"
              >
                {{ group.color }}
              </Badge>
            </TableCell>
            <TableCell class="text-right space-x-2">
              <Button variant="ghost" size="sm" @click="openEditDialog(group.id)">
                {{ t('common.edit') }}
              </Button>
              <Button variant="ghost" size="sm" @click="openDeleteDialog(group.id)">
                {{ t('common.delete') }}
              </Button>
            </TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </div>

    <Dialog v-model:open="isEditDialogOpen">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{{ t('settings.groups.edit') }}</DialogTitle>
        </DialogHeader>

        <div class="grid gap-4 py-4">
          <div class="grid gap-1.5">
            <FloatingInput v-model="formData.name" :label="t('settings.groups.fields.name')" />
          </div>

          <div class="grid gap-1.5">
            <label class="text-xs text-gray-500 font-medium ml-1">{{
              t('settings.groups.fields.color')
            }}</label>
            <div class="flex items-center gap-2">
              <input
                type="color"
                v-model="formData.color"
                class="w-10 h-10 rounded-lg cursor-pointer border border-gray-200 p-0.5"
              />
              <FloatingInput v-model="formData.color" label="Hex" class="flex-1" />
            </div>
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
          <DialogTitle>{{ t('settings.groups.delete') }}</DialogTitle>
        </DialogHeader>
        <p>{{ t('settings.groups.confirmDelete') }}</p>
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
