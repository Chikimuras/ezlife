import { z } from 'zod'

// const timeString = z.string().transform((val) => {
//   if (/^([0-1][0-9]|2[0-3]):[0-5][0-9]$/.test(val)) return val
//   if (/^([0-1][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$/.test(val)) return val.substring(0, 5)
//   if (val.includes('T')) {
//     const timePart = val.split('T')[1]?.split('.')[0]
//     if (timePart) return timePart.substring(0, 5)
//   }
//   return val
// })

const optionalTimeString = z
  .string()
  .nullable()
  .optional()
  .transform((val) => {
    if (!val) return undefined
    if (/^([0-1][0-9]|2[0-3]):[0-5][0-9]$/.test(val)) return val
    if (/^([0-1][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$/.test(val)) return val.substring(0, 5)
    return val
  })

export const TaskListSchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
  color: z.string().nullable().optional(),
  icon: z.string().nullable().optional(),
  position: z.number(),
  taskCount: z.number().default(0),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
})

export const CreateTaskListSchema = z.object({
  name: z.string().min(1),
  color: z.string().optional(),
  icon: z.string().optional(),
  position: z.number().default(0),
})

export const UpdateTaskListSchema = CreateTaskListSchema.partial()

export const TaskSchema = z.object({
  id: z.string().uuid(),
  taskListId: z.string().uuid(),
  categoryId: z.string().uuid().nullable().optional(),
  title: z.string(),
  description: z.string().nullable().optional(),
  status: z.enum(['todo', 'in_progress', 'done']),
  priority: z.enum(['low', 'medium', 'high', 'urgent']),
  dueDate: z.string().nullable().optional(),
  scheduledDate: z.string().nullable().optional(),
  scheduledStartTime: optionalTimeString,
  scheduledEndTime: optionalTimeString,
  estimatedDurationMinutes: z.number().nullable().optional(),
  recurrenceRule: z.string().nullable().optional(),
  exceptionDates: z.array(z.string()).nullable().optional().default([]),
  position: z.number(),
  activityIds: z.array(z.string().uuid()).default([]),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
})

export const CreateTaskSchema = z.object({
  taskListId: z.string().uuid(),
  categoryId: z.string().uuid().optional(),
  title: z.string().min(1),
  description: z.string().optional(),
  priority: z.enum(['low', 'medium', 'high', 'urgent']).default('medium'),
  dueDate: z.string().optional(),
  scheduledDate: z.string().optional(),
  scheduledStartTime: z.string().regex(/^([0-1][0-9]|2[0-3]):[0-5][0-9]$/).optional(),
  scheduledEndTime: z.string().regex(/^([0-1][0-9]|2[0-3]):[0-5][0-9]$/).optional(),
  estimatedDurationMinutes: z.number().positive().optional(),
  recurrenceRule: z.string().optional(),
  exceptionDates: z.array(z.string()).optional(),
  position: z.number().default(0),
})

export const UpdateTaskSchema = CreateTaskSchema.partial().extend({
  status: z.enum(['todo', 'in_progress', 'done']).optional(),
})

export const TaskCompleteSchema = z.object({
  addToTracker: z.boolean().default(false),
  date: z.string().optional(),
  startTime: z.string().regex(/^([0-1][0-9]|2[0-3]):[0-5][0-9]$/).optional(),
  endTime: z.string().regex(/^([0-1][0-9]|2[0-3]):[0-5][0-9]$/).optional(),
  categoryId: z.string().uuid().optional(),
  notes: z.string().optional(),
})

export const ConvertToActivitySchema = z.object({
  date: z.string(),
  startTime: z.string().regex(/^([0-1][0-9]|2[0-3]):[0-5][0-9]$/),
  endTime: z.string().regex(/^([0-1][0-9]|2[0-3]):[0-5][0-9]$/),
  categoryId: z.string().uuid().optional(),
  notes: z.string().optional(),
})

export const TaskActivitySchema = z.object({
  id: z.string().uuid(),
  taskId: z.string().uuid(),
  activityId: z.string().uuid(),
  createdAt: z.string().datetime(),
})

export type TaskList = z.infer<typeof TaskListSchema>
export type CreateTaskList = z.infer<typeof CreateTaskListSchema>
export type UpdateTaskList = z.infer<typeof UpdateTaskListSchema>
export type Task = z.infer<typeof TaskSchema>
export type CreateTask = z.infer<typeof CreateTaskSchema>
export type UpdateTask = z.infer<typeof UpdateTaskSchema>
export type TaskComplete = z.infer<typeof TaskCompleteSchema>
export type ConvertToActivity = z.infer<typeof ConvertToActivitySchema>
export type TaskActivity = z.infer<typeof TaskActivitySchema>
