import { z } from 'zod'

export const GlobalConstraintsSchema = z.object({
  id: z.string().uuid(),
  totalWeeklyHours: z.number().min(0).default(168),
  minSleepHours: z.number().min(0).default(56),
  underutilizationThreshold: z.number().min(0).max(1).default(0.8),
  overutilizationThreshold: z.number().min(1).default(1.2),
  wastedTimeThreshold: z.number().min(0).default(2),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
})

export const UpdateGlobalConstraintsSchema = z.object({
  totalWeeklyHours: z.number().min(0).optional(),
  minSleepHours: z.number().min(0).optional(),
  underutilizationThreshold: z.number().min(0).max(1).optional(),
  overutilizationThreshold: z.number().min(1).optional(),
  wastedTimeThreshold: z.number().min(0).optional(),
})

export type GlobalConstraints = z.infer<typeof GlobalConstraintsSchema>
export type UpdateGlobalConstraints = z.infer<typeof UpdateGlobalConstraintsSchema>
