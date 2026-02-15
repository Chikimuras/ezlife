import { z } from 'zod'

// Time string transformer: accepts HH:mm or HH:mm:ss, returns HH:mm
const timeString = z.string().transform((val) => {
  // If already HH:mm format, return as-is
  if (/^([0-1][0-9]|2[0-3]):[0-5][0-9]$/.test(val)) {
    return val
  }
  // If HH:mm:ss format, strip seconds
  if (/^([0-1][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$/.test(val)) {
    return val.substring(0, 5)
  }
  // If ISO datetime, extract time portion and strip seconds
  if (val.includes('T')) {
    const timePart = val.split('T')[1]?.split('.')[0] // Get HH:mm:ss part
    if (timePart) {
      return timePart.substring(0, 5)
    }
  }
  // Fallback: return as-is (will fail validation if invalid)
  return val
})

export const ActivitySchema = z.object({
  id: z.string().uuid(),
  date: z.string().date(),
  startTime: timeString,
  endTime: timeString,
  categoryId: z.string().uuid(),
  notes: z
    .string()
    .nullable()
    .transform((val) => val ?? undefined),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
})

export const CreateActivitySchema = z.object({
  date: z.string().date(),
  startTime: z.string().regex(/^([0-1][0-9]|2[0-3]):[0-5][0-9]$/),
  endTime: z.string().regex(/^([0-1][0-9]|2[0-3]):[0-5][0-9]$/),
  categoryId: z.string().uuid(),
  notes: z.string().optional(),
})

export const UpdateActivitySchema = CreateActivitySchema.partial()

export type Activity = z.infer<typeof ActivitySchema>
export type CreateActivity = z.infer<typeof CreateActivitySchema>
export type UpdateActivity = z.infer<typeof UpdateActivitySchema>
