<script setup lang="ts">
import { ref, watch, onUnmounted } from 'vue'
import AuthenticatedLayout from '@/components/layouts/AuthenticatedLayout.vue'
import Tabs from '@/components/ui/Tabs.vue'
import TabsContent from '@/components/ui/TabsContent.vue'
import TabsList from '@/components/ui/TabsList.vue'
import TabsTrigger from '@/components/ui/TabsTrigger.vue'
import CategoryManager from '@/components/features/CategoryManager.vue'
import GroupManager from '@/components/features/GroupManager.vue'
import ActivityImporter from '@/components/features/ActivityImporter.vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const STORAGE_KEY = 'settings_active_tab'

// Restore active tab from localStorage or default to 'categories'
const activeTab = ref<string>(localStorage.getItem(STORAGE_KEY) ?? 'categories')

// Persist active tab to localStorage whenever it changes
watch(activeTab, (newTab) => {
  localStorage.setItem(STORAGE_KEY, newTab)
})

// Clear active tab from localStorage when leaving the settings page
onUnmounted(() => {
  localStorage.removeItem(STORAGE_KEY)
})
</script>

<template>
  <AuthenticatedLayout>
    <div class="py-4 px-4">
      <h1 class="text-xl font-semibold mb-4">{{ t('settings.title') }}</h1>

      <tabs v-model="activeTab" class="w-full">
        <tabs-list class="grid w-full grid-cols-3">
          <tabs-trigger value="categories">{{ t('settings.tabs.categories') }}</tabs-trigger>
          <tabs-trigger value="groups">{{ t('settings.tabs.groups') }}</tabs-trigger>
          <tabs-trigger value="import">{{ t('settings.tabs.import') }}</tabs-trigger>
        </tabs-list>

        <tabs-content value="categories">
          <category-manager />
        </tabs-content>

        <tabs-content value="groups">
          <group-manager />
        </tabs-content>

        <tabs-content value="import">
          <activity-importer />
        </tabs-content>
      </tabs>
    </div>
  </AuthenticatedLayout>
</template>
