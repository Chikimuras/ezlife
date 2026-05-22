<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { startRegistration } from '@simplewebauthn/browser'
import type { PublicKeyCredentialCreationOptionsJSON } from '@simplewebauthn/browser'
import { useToast } from '@/composables/useToast'
import { authApi } from '@/lib/api/auth'
import type { PasskeySummary } from '@/lib/api/schemas/auth'
import Button from '@/components/ui/Button.vue'
import Dialog from '@/components/ui/Dialog.vue'
import DialogContent from '@/components/ui/DialogContent.vue'
import DialogFooter from '@/components/ui/DialogFooter.vue'
import DialogHeader from '@/components/ui/DialogHeader.vue'
import DialogTitle from '@/components/ui/DialogTitle.vue'
import Table from '@/components/ui/Table.vue'
import TableBody from '@/components/ui/TableBody.vue'
import TableCell from '@/components/ui/TableCell.vue'
import TableHead from '@/components/ui/TableHead.vue'
import TableHeader from '@/components/ui/TableHeader.vue'
import TableRow from '@/components/ui/TableRow.vue'

const { t, locale } = useI18n()
const { success, error: toastError } = useToast()

const passkeys = ref<PasskeySummary[]>([])
const isLoading = ref(false)
const isAdding = ref(false)
const deletingPasskey = ref<PasskeySummary | null>(null)
const isDeleteDialogOpen = ref(false)
const isDeleting = ref(false)

const formatDate = (value: string | null) => {
  if (!value) return t('settings.passkeys.never')
  try {
    return new Date(value).toLocaleString(locale.value)
  } catch {
    return value
  }
}

const fetchPasskeys = async () => {
  isLoading.value = true
  try {
    const response = await authApi.listPasskeys()
    passkeys.value = response.passkeys
  } catch (err) {
    toastError(t('settings.passkeys.messages.fetchError'))
    console.error('Failed to fetch passkeys', err)
  } finally {
    isLoading.value = false
  }
}

const addPasskey = async () => {
  isAdding.value = true
  try {
    const options =
      (await authApi.getAddPasskeyOptions()) as unknown as PublicKeyCredentialCreationOptionsJSON
    const credential = await startRegistration({ optionsJSON: options })
    await authApi.verifyAddPasskey(credential)
    success(t('settings.passkeys.messages.added'))
    await fetchPasskeys()
  } catch (err) {
    toastError(t('settings.passkeys.messages.addError'))
    console.error('Failed to add passkey', err)
  } finally {
    isAdding.value = false
  }
}

const openDeleteDialog = (passkey: PasskeySummary) => {
  deletingPasskey.value = passkey
  isDeleteDialogOpen.value = true
}

const closeDeleteDialog = () => {
  isDeleteDialogOpen.value = false
  deletingPasskey.value = null
}

const confirmDelete = async () => {
  const passkey = deletingPasskey.value
  if (!passkey) return
  isDeleting.value = true
  try {
    await authApi.deletePasskey(passkey.id)
    success(t('settings.passkeys.messages.deleted'))
    closeDeleteDialog()
    await fetchPasskeys()
  } catch (err) {
    toastError(t('settings.passkeys.messages.deleteError'))
    console.error('Failed to delete passkey', err)
  } finally {
    isDeleting.value = false
  }
}

onMounted(() => {
  fetchPasskeys()
})
</script>

<template>
  <div class="py-4">
    <div class="flex items-center justify-between mb-4">
      <div>
        <h2 class="text-lg font-semibold text-gray-900">
          {{ t('settings.passkeys.title') }}
        </h2>
        <p class="text-sm text-gray-600 mt-1">
          {{ t('settings.passkeys.subtitle') }}
        </p>
      </div>
      <button
        type="button"
        :disabled="isAdding"
        class="px-4 py-2 text-sm font-medium text-white bg-primary-500 hover:bg-primary-600 disabled:opacity-60 disabled:cursor-not-allowed rounded-lg shadow-sm hover:shadow transition-colors"
        @click="addPasskey"
      >
        {{ isAdding ? t('settings.passkeys.adding') : t('settings.passkeys.addButton') }}
      </button>
    </div>

    <div
      v-if="isLoading"
      class="text-center py-8 text-sm text-gray-500"
      data-testid="passkeys-loading"
    >
      {{ t('common.loading') }}
    </div>

    <div
      v-else-if="passkeys.length === 0"
      class="text-center py-8 text-sm text-gray-500 border border-dashed border-gray-200 rounded-lg"
    >
      {{ t('settings.passkeys.empty') }}
    </div>

    <Table v-else class="w-full">
      <table-header>
        <table-row>
          <table-head>{{ t('settings.passkeys.columns.device') }}</table-head>
          <table-head>{{ t('settings.passkeys.columns.createdAt') }}</table-head>
          <table-head>{{ t('settings.passkeys.columns.lastUsed') }}</table-head>
          <table-head class="text-right">{{ t('settings.passkeys.columns.actions') }}</table-head>
        </table-row>
      </table-header>
      <table-body>
        <table-row v-for="passkey in passkeys" :key="passkey.id">
          <table-cell>
            {{ passkey.deviceName ?? t('settings.passkeys.unknownDevice') }}
          </table-cell>
          <table-cell>{{ formatDate(passkey.createdAt) }}</table-cell>
          <table-cell>{{ formatDate(passkey.lastUsedAt) }}</table-cell>
          <table-cell class="text-right">
            <button
              type="button"
              class="px-3 py-1.5 text-sm font-medium text-white bg-red-500 hover:bg-red-600 disabled:opacity-60 disabled:cursor-not-allowed rounded-md shadow-sm hover:shadow transition-colors"
              :disabled="passkeys.length <= 1"
              :title="passkeys.length <= 1 ? t('settings.passkeys.lastOneTooltip') : ''"
              @click="openDeleteDialog(passkey)"
            >
              {{ t('common.delete') }}
            </button>
          </table-cell>
        </table-row>
      </table-body>
    </Table>

    <Dialog v-model:open="isDeleteDialogOpen">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{{ t('settings.passkeys.confirmDelete.title') }}</DialogTitle>
        </DialogHeader>
        <p class="text-sm text-gray-600 py-2">
          {{ t('settings.passkeys.confirmDelete.message') }}
        </p>
        <DialogFooter>
          <Button variant="outline" :disabled="isDeleting" @click="closeDeleteDialog">
            {{ t('common.cancel') }}
          </Button>
          <Button variant="destructive" :disabled="isDeleting" @click="confirmDelete">
            {{ isDeleting ? t('common.loading') : t('common.delete') }}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
</template>
