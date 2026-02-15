import { z } from 'zod'

export const GroupBreakdownItemSchema = z.object({
  groupId: z.string().uuid(),
  groupName: z.string(),
  groupColor: z.string().nullable(),
  minutes: z.number(),
  previousMinutes: z.number(),
  minutesDelta: z.number(),
  percentChange: z.number(),
  percentOfTotal: z.number(),
})

export const TopCategoryItemSchema = z.object({
  categoryId: z.string().uuid(),
  categoryName: z.string(),
  groupName: z.string(),
  groupColor: z.string().nullable(),
  minutes: z.number(),
  previousMinutes: z.number(),
  minutesDelta: z.number(),
  percentChange: z.number(),
  percentOfTotal: z.number(),
})

export const ActivityHighlightSchema = z.object({
  categoryName: z.string(),
  minutes: z.number(),
  startTime: z.string(),
  endTime: z.string(),
})

export const DailyStatsSchema = z.object({
  activitiesCount: z.number(),
  previousActivitiesCount: z.number(),
  activitiesCountDelta: z.number(),
  categoriesUsed: z.number(),
  previousCategoriesUsed: z.number(),
  categoriesUsedDelta: z.number(),
  averageActivityDuration: z.number(),
  previousAverageActivityDuration: z.number(),
  averageActivityDurationDelta: z.number(),
  longestActivity: ActivityHighlightSchema.nullish(),
  shortestActivity: ActivityHighlightSchema.nullish(),
})

export const ProductivitySchema = z.object({
  mandatoryMinutes: z.number(),
  previousMandatoryMinutes: z.number(),
  mandatoryMinutesDelta: z.number(),
  mandatoryPercentOfTotal: z.number(),
})

export const DailyInsightSchema = z.object({
  date: z.string().date(),
  previousDate: z.string().date(),
  totalMinutes: z.number(),
  previousTotalMinutes: z.number(),
  totalMinutesDelta: z.number(),
  totalMinutesPercentChange: z.number(),
  groupBreakdown: z.array(GroupBreakdownItemSchema),
  topCategories: z.array(TopCategoryItemSchema).max(5),
  stats: DailyStatsSchema,
  productivity: ProductivitySchema.nullish(),
})

// Weekly Insights Schemas
export const DailyBreakdownItemSchema = z.object({
  date: z.string().date(),
  dayName: z.string(),
  minutes: z.number(),
  activitiesCount: z.number(),
})

export const ProductiveDaySchema = z.object({
  date: z.string().date(),
  dayName: z.string(),
  minutes: z.number(),
})

export const WeeklyActivityHighlightSchema = z.object({
  categoryName: z.string(),
  minutes: z.number(),
  date: z.string().date(),
  startTime: z.string(),
  endTime: z.string(),
})

export const WeeklyStatsSchema = z.object({
  activitiesCount: z.number(),
  previousActivitiesCount: z.number(),
  activitiesCountDelta: z.number(),
  categoriesUsed: z.number(),
  previousCategoriesUsed: z.number(),
  categoriesUsedDelta: z.number(),
  averageActivityDuration: z.number(),
  previousAverageActivityDuration: z.number(),
  averageActivityDurationDelta: z.number(),
  averageDailyMinutes: z.number(),
  previousAverageDailyMinutes: z.number(),
  averageDailyMinutesDelta: z.number(),
  mostProductiveDay: ProductiveDaySchema.nullish(),
  leastProductiveDay: ProductiveDaySchema.nullish(),
  longestActivity: WeeklyActivityHighlightSchema.nullish(),
})

export const GoalProgressSchema = z.object({
  categoryId: z.string().uuid(),
  categoryName: z.string(),
  currentWeekMinutes: z.number(),
  targetWeeklyMinutes: z.number(),
  minWeeklyMinutes: z.number(),
  maxWeeklyMinutes: z.number(),
  progressPercent: z.number(),
  status: z.enum(['under', 'on_track', 'target_met', 'over']),
})

export const WeeklyInsightSchema = z.object({
  weekStartDate: z.string().date(),
  weekEndDate: z.string().date(),
  previousWeekStartDate: z.string().date(),
  previousWeekEndDate: z.string().date(),
  totalMinutes: z.number(),
  previousTotalMinutes: z.number(),
  totalMinutesDelta: z.number(),
  totalMinutesPercentChange: z.number(),
  groupBreakdown: z.array(GroupBreakdownItemSchema),
  topCategories: z.array(TopCategoryItemSchema).max(5),
  stats: WeeklyStatsSchema,
  dailyBreakdown: z.array(DailyBreakdownItemSchema),
  goalsProgress: z.array(GoalProgressSchema).nullish(),
})

export type GroupBreakdownItem = z.infer<typeof GroupBreakdownItemSchema>
export type TopCategoryItem = z.infer<typeof TopCategoryItemSchema>
export type ActivityHighlight = z.infer<typeof ActivityHighlightSchema>
export type DailyStats = z.infer<typeof DailyStatsSchema>
export type Productivity = z.infer<typeof ProductivitySchema>
export type DailyInsight = z.infer<typeof DailyInsightSchema>
export type DailyBreakdownItem = z.infer<typeof DailyBreakdownItemSchema>
export type ProductiveDay = z.infer<typeof ProductiveDaySchema>
export type WeeklyActivityHighlight = z.infer<typeof WeeklyActivityHighlightSchema>
export type WeeklyStats = z.infer<typeof WeeklyStatsSchema>
export type GoalProgress = z.infer<typeof GoalProgressSchema>
export type WeeklyInsight = z.infer<typeof WeeklyInsightSchema>
