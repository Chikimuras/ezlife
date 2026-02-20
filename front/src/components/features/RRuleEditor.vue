<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { RRule, Frequency, type Options } from 'rrule'
import { cn } from '@/lib/utils/cn'
import Label from '@/components/ui/Label.vue'
import Input from '@/components/ui/Input.vue'
import Select from '@/components/ui/Select.vue'
import SelectTrigger from '@/components/ui/SelectTrigger.vue'
import SelectValue from '@/components/ui/SelectValue.vue'
import SelectContent from '@/components/ui/SelectContent.vue'
import SelectItem from '@/components/ui/SelectItem.vue'
import Button from '@/components/ui/Button.vue'
import { X, Calendar as CalendarIcon, Plus } from 'lucide-vue-next'

const props = defineProps<{
  modelValue: string | undefined
  exdates?: string[]
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string | undefined]
  'update:exdates': [value: string[]]
}>()

const { t } = useI18n()

// --- State ---

const frequency = ref<Frequency | null>(null)
const interval = ref<number>(1)

// Weekly
const byWeekday = ref<number[]>([]) // 0=MO, 6=SU (RRule constants)

// Monthly
const monthlyMode = ref<'dayOfMonth' | 'onThe'>('dayOfMonth')
const dayOfMonth = ref<number>(1)
const setPos = ref<number>(1) // 1, 2, 3, 4, -1
const weekdayForPos = ref<number>(0) // 0=MO

// Yearly
const byMonth = ref<number[]>([]) // 1=Jan, 12=Dec
const yearDayOfMonth = ref<number>(1)

// End
const endMode = ref<'never' | 'count' | 'until'>('never')
const endCount = ref<number>(10)
const endDate = ref<string>('') // YYYY-MM-DD

// Exceptions
const newExdate = ref<string>('')

// --- Options for Selects ---

const frequencies = computed(() => [
  { value: 'none', label: t('tasks.recurrence.frequencies.none') },
  { value: Frequency.DAILY.toString(), label: t('tasks.recurrence.frequencies.daily') },
  { value: Frequency.WEEKLY.toString(), label: t('tasks.recurrence.frequencies.weekly') },
  { value: Frequency.MONTHLY.toString(), label: t('tasks.recurrence.frequencies.monthly') },
  { value: Frequency.YEARLY.toString(), label: t('tasks.recurrence.frequencies.yearly') },
])

const weekDays = computed(() => [
  { value: RRule.MO.weekday, label: t('tasks.recurrence.days.mo') },
  { value: RRule.TU.weekday, label: t('tasks.recurrence.days.tu') },
  { value: RRule.WE.weekday, label: t('tasks.recurrence.days.we') },
  { value: RRule.TH.weekday, label: t('tasks.recurrence.days.th') },
  { value: RRule.FR.weekday, label: t('tasks.recurrence.days.fr') },
  { value: RRule.SA.weekday, label: t('tasks.recurrence.days.sa') },
  { value: RRule.SU.weekday, label: t('tasks.recurrence.days.su') },
])

const months = computed(() => [
  { value: 1, label: 'Jan' },
  { value: 2, label: 'Feb' },
  { value: 3, label: 'Mar' },
  { value: 4, label: 'Apr' },
  { value: 5, label: 'May' },
  { value: 6, label: 'Jun' },
  { value: 7, label: 'Jul' },
  { value: 8, label: 'Aug' },
  { value: 9, label: 'Sep' },
  { value: 10, label: 'Oct' },
  { value: 11, label: 'Nov' },
  { value: 12, label: 'Dec' },
])

const positions = computed(() => [
  { value: 1, label: t('tasks.recurrence.monthly.positions.1') },
  { value: 2, label: t('tasks.recurrence.monthly.positions.2') },
  { value: 3, label: t('tasks.recurrence.monthly.positions.3') },
  { value: 4, label: t('tasks.recurrence.monthly.positions.4') },
  { value: -1, label: t('tasks.recurrence.monthly.positions.-1') },
])

// --- Helpers ---

const toggleWeekday = (day: number) => {
  if (byWeekday.value.includes(day)) {
    byWeekday.value = byWeekday.value.filter((d) => d !== day)
  } else {
    byWeekday.value = [...byWeekday.value, day]
  }
}

const toggleMonth = (month: number) => {
  if (byMonth.value.includes(month)) {
    byMonth.value = byMonth.value.filter((m) => m !== month)
  } else {
    byMonth.value = [...byMonth.value, month]
  }
}

const addExdate = () => {
  if (!newExdate.value) return
  const currentExdates = props.exdates || []
  if (!currentExdates.includes(newExdate.value)) {
    emit('update:exdates', [...currentExdates, newExdate.value])
  }
  newExdate.value = ''
}

const removeExdate = (dateStr: string) => {
  const currentExdates = props.exdates || []
  emit('update:exdates', currentExdates.filter((d) => d !== dateStr))
}

// --- RRULE Logic ---

const buildRRule = (): string | undefined => {
  if (frequency.value === null) return undefined

  const options: Partial<Options> = {
    freq: frequency.value,
    interval: Math.max(1, interval.value),
  }

  // Weekly
  if (frequency.value === Frequency.WEEKLY && byWeekday.value.length > 0) {
    options.byweekday = byWeekday.value
  }

  // Monthly
  if (frequency.value === Frequency.MONTHLY) {
    if (monthlyMode.value === 'dayOfMonth') {
      options.bymonthday = [dayOfMonth.value]
    } else {
      options.bysetpos = [setPos.value]
      options.byweekday = [weekdayForPos.value]
    }
  }

  // Yearly
  if (frequency.value === Frequency.YEARLY) {
    if (byMonth.value.length > 0) {
      options.bymonth = byMonth.value
    }
    options.bymonthday = [yearDayOfMonth.value]
  }

  // End conditions
  if (endMode.value === 'count') {
    options.count = Math.max(1, endCount.value)
  } else if (endMode.value === 'until' && endDate.value) {
    options.until = new Date(endDate.value)
    // Adjust to end of day? Usually 'until' is inclusive.
    // Let's set it to end of day to be safe or keep as is (00:00).
    // Standard practice often uses end of day for inclusive end dates.
    options.until.setHours(23, 59, 59, 999) 
  }

  try {
    return new RRule(options).toString()
  } catch (e) {
    console.error('Invalid RRule options', e)
    return undefined
  }
}

const parseRRule = (rruleStr: string) => {
  try {
    const rule = RRule.fromString(rruleStr)
    const opts = rule.options

    frequency.value = opts.freq
    interval.value = opts.interval || 1

    // Weekly
    if (opts.byweekday) {
      // rrule.js stores byweekday as RRule.MO, etc. or integer.
      // normalize to integers
      byWeekday.value = opts.byweekday.map((d: any) => (typeof d === 'number' ? d : d.weekday))
    } else {
      byWeekday.value = []
    }

    // Monthly
    if (opts.bysetpos && opts.bysetpos.length > 0) {
      monthlyMode.value = 'onThe'
      const pos = opts.bysetpos[0]
      if (pos !== undefined) {
        setPos.value = pos
      }
      if (opts.byweekday && opts.byweekday.length > 0) {
        const wd = opts.byweekday[0] as any
        if (wd !== undefined) {
          weekdayForPos.value = typeof wd === 'number' ? wd : wd.weekday
        }
      }
    } else {
      monthlyMode.value = 'dayOfMonth'
      if (opts.bymonthday && opts.bymonthday.length > 0) {
        const d = opts.bymonthday[0]
        if (d !== undefined) {
          dayOfMonth.value = d
        }
      }
    }

    // Yearly
    if (opts.bymonth) {
      byMonth.value = Array.isArray(opts.bymonth) ? opts.bymonth : [opts.bymonth]
    } else {
      byMonth.value = []
    }
    if (opts.bymonthday && opts.bymonthday.length > 0) {
      const d = opts.bymonthday[0]
      if (d !== undefined) {
        yearDayOfMonth.value = d
      }
    }

    // End
    if (opts.count) {
      endMode.value = 'count'
      endCount.value = opts.count
    } else if (opts.until) {
      endMode.value = 'until'
      // Convert date to YYYY-MM-DD
      const d = opts.until
      const year = d.getFullYear()
      const month = String(d.getMonth() + 1).padStart(2, '0')
      const day = String(d.getDate()).padStart(2, '0')
      endDate.value = `${year}-${month}-${day}`
    } else {
      endMode.value = 'never'
    }
  } catch (e) {
    console.error('Failed to parse RRule', e)
    // Reset to defaults if invalid
    frequency.value = null
  }
}

// Watchers
watch(
  [
    frequency,
    interval,
    byWeekday,
    monthlyMode,
    dayOfMonth,
    setPos,
    weekdayForPos,
    byMonth,
    yearDayOfMonth,
    endMode,
    endCount,
    endDate,
  ],
  () => {
    const newVal = buildRRule()
    if (newVal !== props.modelValue) {
      emit('update:modelValue', newVal)
    }
  },
  { deep: true },
)

watch(
  () => props.modelValue,
  (newVal) => {
    if (newVal) {
      // Avoid re-parsing if the value matches what we just built (to prevent cycles/resets)
      const currentBuilt = buildRRule()
      if (newVal !== currentBuilt) {
        parseRRule(newVal)
      }
    } else {
      frequency.value = null
    }
  },
  { immediate: true },
)

const previewDates = computed(() => {
  const rruleStr = buildRRule()
  if (!rruleStr) return []
  try {
    const rule = RRule.fromString(rruleStr)
    // Use dtstart of today for preview purposes
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    const ruleWithStart = new RRule({ ...rule.options, dtstart: today })
    return ruleWithStart.all((_, i) => i < 5)
  } catch {
    return []
  }
})

const formatDate = (date: Date) => {
  return new Intl.DateTimeFormat('default', {
    weekday: 'short',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(date)
}
</script>

<template>
  <div class="bg-gray-50 rounded-lg border border-gray-100 p-4 space-y-4">
    <!-- 1. Frequency & Interval -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div class="space-y-2">
        <Label>{{ t('tasks.recurrence.frequency') }}</Label>
        <Select
          :model-value="frequency?.toString() || 'none'"
          @update:model-value="(v) => (frequency = v === 'none' ? null : Number(v))"
        >
          <SelectTrigger class="bg-white">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem v-for="f in frequencies" :key="f.value" :value="f.value">
              {{ f.label }}
            </SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div v-if="frequency !== null" class="space-y-2">
        <Label>{{ t('tasks.recurrence.interval') }}</Label>
        <div class="flex items-center gap-2">
          <Input type="number" v-model.number="interval" min="1" class="bg-white" />
          <span class="text-sm text-gray-500">
            {{
              frequency === Frequency.DAILY
                ? t('tasks.recurrence.frequencies.daily')
                : frequency === Frequency.WEEKLY
                  ? t('tasks.recurrence.frequencies.weekly')
                  : frequency === Frequency.MONTHLY
                    ? t('tasks.recurrence.frequencies.monthly')
                    : t('tasks.recurrence.frequencies.yearly')
            }}
          </span>
        </div>
      </div>
    </div>

    <template v-if="frequency !== null">
      <!-- 2. Weekly Options -->
      <div v-if="frequency === Frequency.WEEKLY" class="space-y-2">
        <Label class="text-xs font-semibold text-gray-500 uppercase tracking-wide">
          {{ t('tasks.recurrence.weekly.days') || 'Repeat on' }}
        </Label>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="day in weekDays"
            :key="day.value"
            type="button"
            @click="toggleWeekday(day.value)"
            :class="
              cn(
                'px-3 py-1.5 rounded-full text-xs font-medium border transition-all',
                byWeekday.includes(day.value)
                  ? 'bg-primary-500 text-white border-primary-500 shadow-sm'
                  : 'bg-white text-gray-600 border-gray-200 hover:border-primary-300',
              )
            "
          >
            {{ day.label }}
          </button>
        </div>
      </div>

      <!-- 3. Monthly Options -->
      <div v-if="frequency === Frequency.MONTHLY" class="space-y-3">
        <Label class="text-xs font-semibold text-gray-500 uppercase tracking-wide">
          {{ t('tasks.recurrence.monthly.label') || 'Repeat on' }}
        </Label>
        <div class="space-y-2">
          <!-- Option 1: Day of month -->
          <div class="flex items-center gap-2">
            <input
              type="radio"
              id="monthly-day"
              value="dayOfMonth"
              v-model="monthlyMode"
              class="w-4 h-4 accent-primary-500"
            />
            <label for="monthly-day" class="text-sm text-gray-700 flex items-center gap-2">
              {{ t('tasks.recurrence.monthly.onDay') }}
              <Input
                type="number"
                v-model.number="dayOfMonth"
                min="1"
                max="31"
                class="w-16 h-8 bg-white"
                :disabled="monthlyMode !== 'dayOfMonth'"
              />
            </label>
          </div>

          <!-- Option 2: On the... -->
          <div class="flex items-center gap-2">
            <input
              type="radio"
              id="monthly-pos"
              value="onThe"
              v-model="monthlyMode"
              class="w-4 h-4 accent-primary-500"
            />
            <label for="monthly-pos" class="text-sm text-gray-700 flex flex-wrap items-center gap-2">
              {{ t('tasks.recurrence.monthly.onThe') }}
              <select
                v-model="setPos"
                class="h-8 rounded-md border-gray-200 text-sm focus:border-primary-500 focus:ring-primary-500 bg-white"
                :disabled="monthlyMode !== 'onThe'"
              >
                <option v-for="p in positions" :key="p.value" :value="p.value">
                  {{ p.label }}
                </option>
              </select>
              <select
                v-model="weekdayForPos"
                class="h-8 rounded-md border-gray-200 text-sm focus:border-primary-500 focus:ring-primary-500 bg-white"
                :disabled="monthlyMode !== 'onThe'"
              >
                <option v-for="d in weekDays" :key="d.value" :value="d.value">
                  {{ d.label }}
                </option>
              </select>
            </label>
          </div>
        </div>
      </div>

      <!-- 4. Yearly Options -->
      <div v-if="frequency === Frequency.YEARLY" class="space-y-3">
        <div class="space-y-2">
           <Label class="text-xs font-semibold text-gray-500 uppercase tracking-wide">
             {{ t('tasks.recurrence.yearly.months') }}
           </Label>
           <div class="flex flex-wrap gap-1.5">
              <button
                v-for="m in months"
                :key="m.value"
                type="button"
                @click="toggleMonth(m.value)"
                :class="
                  cn(
                    'px-2 py-1 rounded-md text-xs font-medium border transition-all',
                     byMonth.includes(m.value)
                      ? 'bg-primary-500 text-white border-primary-500 shadow-sm'
                      : 'bg-white text-gray-600 border-gray-200 hover:border-primary-300',
                  )
                "
              >
                {{ m.label }}
              </button>
           </div>
        </div>
        <div class="flex items-center gap-2">
             <Label class="text-sm text-gray-700 whitespace-nowrap">{{ t('tasks.recurrence.yearly.onDay') }}</Label>
             <Input type="number" v-model.number="yearDayOfMonth" min="1" max="31" class="w-20 bg-white" />
        </div>
      </div>

      <!-- 5. End Condition -->
      <div class="pt-2 border-t border-gray-200 space-y-2">
        <Label class="text-xs font-semibold text-gray-500 uppercase tracking-wide">
          {{ t('tasks.recurrence.end.label') }}
        </Label>
        <div class="space-y-2">
          <div class="flex items-center gap-2">
            <input
              type="radio"
              id="end-never"
              value="never"
              v-model="endMode"
              class="w-4 h-4 accent-primary-500"
            />
            <label for="end-never" class="text-sm text-gray-700">{{ t('tasks.recurrence.end.never') }}</label>
          </div>

          <div class="flex items-center gap-2">
            <input
              type="radio"
              id="end-count"
              value="count"
              v-model="endMode"
              class="w-4 h-4 accent-primary-500"
            />
            <label for="end-count" class="text-sm text-gray-700 flex items-center gap-2">
              {{ t('tasks.recurrence.end.after') }}
              <Input
                type="number"
                v-model.number="endCount"
                min="1"
                class="w-20 h-8 bg-white"
                :disabled="endMode !== 'count'"
              />
              {{ t('tasks.recurrence.end.occurrences') }}
            </label>
          </div>

          <div class="flex items-center gap-2">
            <input
              type="radio"
              id="end-until"
              value="until"
              v-model="endMode"
              class="w-4 h-4 accent-primary-500"
            />
            <label for="end-until" class="text-sm text-gray-700 flex items-center gap-2">
              {{ t('tasks.recurrence.end.until') }}
              <Input
                type="date"
                v-model="endDate"
                class="w-auto h-8 bg-white"
                :disabled="endMode !== 'until'"
              />
            </label>
          </div>
        </div>
      </div>

      <!-- 6. Exceptions (Exdate) -->
      <div class="pt-2 border-t border-gray-200 space-y-2">
         <Label class="text-xs font-semibold text-gray-500 uppercase tracking-wide">
          {{ t('tasks.recurrence.exceptions.label') }}
        </Label>
        <div class="flex items-center gap-2">
           <Input type="date" v-model="newExdate" class="bg-white" />
           <Button type="button" variant="outline" size="sm" @click="addExdate" :disabled="!newExdate">
              <Plus class="w-4 h-4 mr-1" />
              {{ t('common.add') }}
           </Button>
        </div>
        
        <div v-if="exdates && exdates.length > 0" class="flex flex-wrap gap-2 mt-2">
           <span v-for="date in exdates" :key="date" class="inline-flex items-center gap-1 px-2 py-1 bg-red-50 text-red-600 border border-red-100 rounded-full text-xs font-medium">
              {{ date }}
              <button type="button" @click="removeExdate(date)" class="hover:text-red-800 focus:outline-none">
                 <X class="w-3 h-3" />
              </button>
           </span>
        </div>
        <div v-else class="text-xs text-gray-400 italic">
           {{ t('tasks.recurrence.exceptions.noExceptions') }}
        </div>
      </div>

      <!-- 7. Preview -->
      <div class="mt-3 bg-white rounded-md border border-gray-200 p-3 shadow-sm">
        <Label class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2 block">
          {{ t('tasks.recurrence.preview.label') }}
        </Label>
        <ul v-if="previewDates.length > 0" class="space-y-1">
          <li v-for="(date, i) in previewDates" :key="i" class="text-sm text-gray-600 flex items-center gap-2">
            <CalendarIcon class="w-3.5 h-3.5 text-primary-500" />
            {{ formatDate(date) }}
          </li>
        </ul>
        <p v-else class="text-xs text-gray-400 italic">
          {{ t('tasks.recurrence.preview.noPreview') }}
        </p>
      </div>
    </template>
  </div>
</template>
