import { z } from 'zod'

export const GroupSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1),
  color: z.string().optional(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
})

export const CreateGroupSchema = z.object({
  name: z.string().min(1),
  color: z.string().optional(),
})

export const UpdateGroupSchema = CreateGroupSchema.partial()

export type Group = z.infer<typeof GroupSchema>
export type CreateGroup = z.infer<typeof CreateGroupSchema>
export type UpdateGroup = z.infer<typeof UpdateGroupSchema>
