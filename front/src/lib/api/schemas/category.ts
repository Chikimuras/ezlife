import { z } from 'zod'

export const CategorySchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1),
  groupId: z.string().uuid(),
  priority: z.number().int().min(1),
  minWeeklyHours: z.number().min(0),
  targetWeeklyHours: z.number().min(0),
  maxWeeklyHours: z.number().min(0),
  unit: z.enum(['hours', 'minutes', 'count']),
  mandatory: z.boolean(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
})

export const CreateCategorySchema = z.object({
  name: z.string().min(1),
  groupId: z.string().uuid(),
  priority: z.number().int().min(1).default(1),
  minWeeklyHours: z.number().min(0).default(0),
  targetWeeklyHours: z.number().min(0).default(0),
  maxWeeklyHours: z.number().min(0).default(0),
  unit: z.enum(['hours', 'minutes', 'count']).default('hours'),
  mandatory: z.boolean().default(false),
})

export const UpdateCategorySchema = CreateCategorySchema.partial()

export type Category = z.infer<typeof CategorySchema>
export type CreateCategory = z.infer<typeof CreateCategorySchema>
export type UpdateCategory = z.infer<typeof UpdateCategorySchema>
