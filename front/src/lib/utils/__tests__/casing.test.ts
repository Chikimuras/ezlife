import { describe, it, expect } from 'vitest'
import { toCamelCase } from '../casing'

describe('toCamelCase', () => {
  it('should convert snake_case keys to camelCase', () => {
    const input = {
      access_token: 'token',
      user_id: '123',
      is_active: true,
    }

    const result = toCamelCase(input)

    expect(result).toEqual({
      accessToken: 'token',
      userId: '123',
      isActive: true,
    })
  })

  it('should handle nested objects', () => {
    const input = {
      user_info: {
        user_id: '123',
        created_at: '2024-01-25',
      },
    }

    const result = toCamelCase(input)

    expect(result).toEqual({
      userInfo: {
        userId: '123',
        createdAt: '2024-01-25',
      },
    })
  })

  it('should handle arrays of objects', () => {
    const input = {
      user_list: [
        { user_id: '1', user_name: 'Alice' },
        { user_id: '2', user_name: 'Bob' },
      ],
    }

    const result = toCamelCase(input)

    expect(result).toEqual({
      userList: [
        { userId: '1', userName: 'Alice' },
        { userId: '2', userName: 'Bob' },
      ],
    })
  })

  it('should preserve camelCase keys', () => {
    const input = {
      accessToken: 'token',
      userId: '123',
    }

    const result = toCamelCase(input)

    expect(result).toEqual({
      accessToken: 'token',
      userId: '123',
    })
  })

  it('should handle empty objects', () => {
    const input = {}

    const result = toCamelCase(input)

    expect(result).toEqual({})
  })

  it('should handle null values', () => {
    const input = {
      user_id: null,
      created_at: null,
    }

    const result = toCamelCase(input)

    expect(result).toEqual({
      userId: null,
      createdAt: null,
    })
  })

  it('should handle primitive values', () => {
    expect(toCamelCase('string')).toBe('string')
    expect(toCamelCase(123)).toBe(123)
    expect(toCamelCase(true)).toBe(true)
    expect(toCamelCase(null)).toBe(null)
  })

  it('should handle deeply nested structures', () => {
    const input = {
      user_data: {
        user_profile: {
          first_name: 'John',
          last_name: 'Doe',
          contact_info: {
            email_address: 'john@example.com',
          },
        },
      },
    }

    const result = toCamelCase(input)

    expect(result).toEqual({
      userData: {
        userProfile: {
          firstName: 'John',
          lastName: 'Doe',
          contactInfo: {
            emailAddress: 'john@example.com',
          },
        },
      },
    })
  })

  it('should handle mixed arrays', () => {
    const input = {
      mixed_array: [1, 'string', { user_id: '123' }, true, null],
    }

    const result = toCamelCase(input)

    expect(result).toEqual({
      mixedArray: [1, 'string', { userId: '123' }, true, null],
    })
  })
})
