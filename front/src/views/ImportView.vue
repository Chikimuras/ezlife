<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import AuthenticatedLayout from '@/components/layouts/AuthenticatedLayout.vue'
import Button from '@/components/ui/Button.vue'
import { importApi, type ImportResponse } from '@/lib/api/import'
import { useToast } from '@/composables/useToast'

const { t } = useI18n()
const router = useRouter()
const { success, error } = useToast()

const selectedFile = ref<File | null>(null)
const isUploading = ref(false)
const isDragging = ref(false)
const importResult = ref<ImportResponse | null>(null)
const uploadError = ref<string | null>(null)

const fileInputRef = ref<HTMLInputElement | null>(null)

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    const file = target.files[0]
    if (file && isValidFile(file)) {
      selectedFile.value = file
      importResult.value = null
      uploadError.value = null
    } else {
      error(t('import.errors.invalidFileType'))
    }
  }
}

const handleDrop = (event: DragEvent) => {
  isDragging.value = false
  event.preventDefault()

  if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
    const file = event.dataTransfer.files[0]
    if (file && isValidFile(file)) {
      selectedFile.value = file
      importResult.value = null
      uploadError.value = null
    } else {
      error(t('import.errors.invalidFileType'))
    }
  }
}

const handleDragOver = (event: DragEvent) => {
  event.preventDefault()
  isDragging.value = true
}

const handleDragLeave = () => {
  isDragging.value = false
}

const isValidFile = (file: File): boolean => {
  const validExtensions = ['.xlsx', '.xls']
  const fileName = file.name.toLowerCase()
  return validExtensions.some((ext) => fileName.endsWith(ext))
}

const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

const handleUpload = async () => {
  if (!selectedFile.value) return

  isUploading.value = true
  uploadError.value = null

  try {
    const result = await importApi.uploadExcel(selectedFile.value)
    importResult.value = result

    if (result.errors.length === 0) {
      success(t('import.messages.success'))
    } else {
      error(t('import.messages.partialSuccess'))
    }
  } catch (err) {
    uploadError.value = err instanceof Error ? err.message : t('import.errors.uploadFailed')
    error(t('import.errors.uploadFailed'))
  } finally {
    isUploading.value = false
  }
}

const handleReset = () => {
  selectedFile.value = null
  importResult.value = null
  uploadError.value = null
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
}

const navigateToActivities = () => {
  router.push('/activities')
}

const triggerFileInput = () => {
  fileInputRef.value?.click()
}
</script>

<template>
  <AuthenticatedLayout>
    <div class="h-full flex flex-col bg-gray-50">
      <div class="bg-white border-b border-gray-200 px-4 py-4">
        <h1 class="text-xl font-semibold">{{ t('import.title') }}</h1>
        <p class="text-sm text-gray-600 mt-1">{{ t('import.description') }}</p>
      </div>

      <div class="flex-1 overflow-auto">
        <div class="max-w-2xl mx-auto p-4">
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <!-- Upload Area -->
            <div v-if="!importResult" class="space-y-4">
              <!-- Drag & Drop Zone -->
              <div
                class="border-2 border-dashed rounded-lg p-8 text-center transition-colors"
                :class="{
                  'border-primary-500 bg-primary-50': isDragging,
                  'border-gray-300 hover:border-gray-400': !isDragging,
                }"
                @drop="handleDrop"
                @dragover="handleDragOver"
                @dragleave="handleDragLeave"
              >
                <div class="flex flex-col items-center gap-3">
                  <!-- Upload Icon -->
                  <svg
                    class="w-12 h-12 text-gray-400"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                    />
                  </svg>

                  <div>
                    <p class="text-sm text-gray-600 mb-2">
                      {{ t('import.dropZone.description') }}
                    </p>
                    <Button variant="outline" size="sm" @click="triggerFileInput">
                      {{ t('import.dropZone.browse') }}
                    </Button>
                    <input
                      ref="fileInputRef"
                      type="file"
                      accept=".xlsx,.xls"
                      class="hidden"
                      @change="handleFileSelect"
                    />
                  </div>

                  <p class="text-xs text-gray-500">{{ t('import.dropZone.formats') }}</p>
                </div>
              </div>

              <!-- Selected File Info -->
              <div
                v-if="selectedFile"
                class="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200"
              >
                <div class="flex items-center gap-3">
                  <svg
                    class="w-8 h-8 text-green-600"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                  <div>
                    <p class="text-sm font-medium text-gray-900">{{ selectedFile.name }}</p>
                    <p class="text-xs text-gray-500">{{ formatFileSize(selectedFile.size) }}</p>
                  </div>
                </div>
                <Button variant="ghost" size="sm" @click="handleReset">
                  <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </Button>
              </div>

              <!-- Upload Button -->
              <Button class="w-full" :disabled="!selectedFile || isUploading" @click="handleUpload">
                <svg
                  v-if="isUploading"
                  class="animate-spin -ml-1 mr-2 h-4 w-4"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    class="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    stroke-width="4"
                  ></circle>
                  <path
                    class="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                {{ isUploading ? t('import.uploading') : t('import.upload') }}
              </Button>

              <!-- Upload Error -->
              <div
                v-if="uploadError"
                class="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-800"
              >
                {{ uploadError }}
              </div>
            </div>

            <!-- Results Display -->
            <div v-else class="space-y-4">
              <!-- Success Message -->
              <div
                class="flex items-start gap-3 p-4 rounded-lg"
                :class="{
                  'bg-green-50 border border-green-200': importResult.errors.length === 0,
                  'bg-yellow-50 border border-yellow-200': importResult.errors.length > 0,
                }"
              >
                <svg
                  class="w-6 h-6 flex-shrink-0"
                  :class="{
                    'text-green-600': importResult.errors.length === 0,
                    'text-yellow-600': importResult.errors.length > 0,
                  }"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <div>
                  <p
                    class="font-semibold"
                    :class="{
                      'text-green-900': importResult.errors.length === 0,
                      'text-yellow-900': importResult.errors.length > 0,
                    }"
                  >
                    {{
                      importResult.errors.length === 0
                        ? t('import.results.success')
                        : t('import.results.partialSuccess')
                    }}
                  </p>
                  <ul class="mt-2 space-y-1 text-sm">
                    <li
                      :class="{
                        'text-green-800': importResult.errors.length === 0,
                        'text-yellow-800': importResult.errors.length > 0,
                      }"
                    >
                      {{ t('import.results.groupsCreated', { count: importResult.groupsCreated }) }}
                    </li>
                    <li
                      :class="{
                        'text-green-800': importResult.errors.length === 0,
                        'text-yellow-800': importResult.errors.length > 0,
                      }"
                    >
                      {{
                        t('import.results.categoriesCreated', {
                          count: importResult.categoriesCreated,
                        })
                      }}
                    </li>
                    <li
                      :class="{
                        'text-green-800': importResult.errors.length === 0,
                        'text-yellow-800': importResult.errors.length > 0,
                      }"
                    >
                      {{
                        t('import.results.activitiesCreated', {
                          count: importResult.activitiesCreated,
                        })
                      }}
                    </li>
                  </ul>
                </div>
              </div>

              <!-- Errors List -->
              <div
                v-if="importResult.errors.length > 0"
                class="p-4 bg-red-50 border border-red-200 rounded-lg"
              >
                <p class="font-semibold text-red-900 mb-2">{{ t('import.results.errors') }}</p>
                <ul class="list-disc list-inside space-y-1 text-sm text-red-800">
                  <li v-for="(err, index) in importResult.errors" :key="index">{{ err }}</li>
                </ul>
              </div>

              <!-- Action Buttons -->
              <div class="flex gap-3">
                <Button variant="outline" class="flex-1" @click="handleReset">
                  {{ t('import.actions.importAnother') }}
                </Button>
                <Button class="flex-1" @click="navigateToActivities">
                  {{ t('import.actions.viewActivities') }}
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AuthenticatedLayout>
</template>
