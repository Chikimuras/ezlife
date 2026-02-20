<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useGlobalConstraintsStore } from '@/stores/globalConstraints'
import { useI18n } from 'vue-i18n'
import { useToast } from '@/composables/useToast'
import Button from '@/components/ui/Button.vue'
import FloatingInput from '@/components/ui/FloatingInput.vue'
import type { UpdateGlobalConstraints } from '@/lib/api/schemas/globalConstraints'

const { t } = useI18n()
const { success, error } = useToast()
const constraintsStore = useGlobalConstraintsStore()

const formData = ref<UpdateGlobalConstraints>({
  totalWeeklyHours: 168,
  minSleepHours: 56,
  underutilizationThreshold: 0.8,
  overutilizationThreshold: 1.2,
  wastedTimeThreshold: 2,
})

const isSaving = ref(false)

onMounted(async () => {
  await constraintsStore.fetchConstraints()

  if (constraintsStore.constraints) {
    formData.value = {
      totalWeeklyHours: constraintsStore.constraints.totalWeeklyHours,
      minSleepHours: constraintsStore.constraints.minSleepHours,
      underutilizationThreshold: constraintsStore.constraints.underutilizationThreshold,
      overutilizationThreshold: constraintsStore.constraints.overutilizationThreshold,
      wastedTimeThreshold: constraintsStore.constraints.wastedTimeThreshold,
    }
  }
})

watch(
  () => constraintsStore.constraints,
  (newConstraints) => {
    if (newConstraints) {
      formData.value = {
        totalWeeklyHours: newConstraints.totalWeeklyHours,
        minSleepHours: newConstraints.minSleepHours,
        underutilizationThreshold: newConstraints.underutilizationThreshold,
        overutilizationThreshold: newConstraints.overutilizationThreshold,
        wastedTimeThreshold: newConstraints.wastedTimeThreshold,
      }
    }
  },
)

const handleSave = async () => {
  isSaving.value = true
  try {
    await constraintsStore.updateConstraints(formData.value)
    success(t('settings.constraints.messages.updated'))
  } catch (err) {
    error(t('settings.constraints.messages.updateError'))
  } finally {
    isSaving.value = false
  }
}
</script>

<template>
  <div class="space-y-4">
    <h2 class="text-sm font-semibold">{{ t('settings.constraints.title') }}</h2>

    <div v-if="constraintsStore.loading && !constraintsStore.constraints" class="text-center py-4">
      {{ t('common.loading') }}
    </div>

    <div v-else-if="constraintsStore.error" class="text-red-500 py-4">
      {{ constraintsStore.error }}
      <Button @click="constraintsStore.fetchConstraints()" variant="outline" class="ml-4">
        {{ t('common.retry') }}
      </Button>
    </div>

    <div v-else class="max-w-2xl border rounded-lg p-4 space-y-6">
      <div class="grid gap-4">
        <div class="grid gap-1.5">
          <FloatingInput
            v-model.number="formData.totalWeeklyHours"
            :label="t('settings.constraints.fields.totalWeekly')"
            type="number"
            min="0"
            :disabled="isSaving"
          />
          <p class="text-xs text-gray-400">
            Nombre d'heures dans une semaine (défaut: 168h = 7j × 24h)
          </p>
        </div>

        <div class="grid gap-1.5">
          <FloatingInput
            v-model.number="formData.minSleepHours"
            :label="t('settings.constraints.fields.minSleep')"
            type="number"
            min="0"
            :disabled="isSaving"
          />
          <p class="text-xs text-gray-400">
            Heures minimales de sommeil par semaine (défaut: 56h = 8h/jour)
          </p>
        </div>

        <div class="grid gap-1.5">
          <FloatingInput
            v-model.number="formData.underutilizationThreshold"
            :label="t('settings.constraints.fields.underutilization')"
            type="number"
            min="0"
            max="1"
            :disabled="isSaving"
          />
          <p class="text-xs text-gray-400">Seuil de sous-utilisation (0.80 = 80%)</p>
        </div>

        <div class="grid gap-1.5">
          <FloatingInput
            v-model.number="formData.overutilizationThreshold"
            :label="t('settings.constraints.fields.overutilization')"
            type="number"
            min="1"
            :disabled="isSaving"
          />
          <p class="text-xs text-gray-400">Seuil de sur-utilisation (1.20 = 120%)</p>
        </div>

        <div class="grid gap-1.5">
          <FloatingInput
            v-model.number="formData.wastedTimeThreshold"
            :label="t('settings.constraints.fields.wastedTime')"
            type="number"
            min="0"
            :disabled="isSaving"
          />
          <p class="text-xs text-gray-400">Seuil de temps perdu (en heures)</p>
        </div>
      </div>

      <div class="flex justify-end">
        <Button @click="handleSave" :disabled="isSaving">
          {{ isSaving ? t('common.loading') : t('settings.constraints.save') }}
        </Button>
      </div>
    </div>
  </div>
</template>
