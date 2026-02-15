type CamelCase<S extends string> = S extends `${infer P1}_${infer P2}${infer P3}`
  ? `${Lowercase<P1>}${Uppercase<P2>}${CamelCase<P3>}`
  : Lowercase<S>

type KeysToCamelCase<T> = {
  [K in keyof T as CamelCase<string & K>]: T[K] extends Record<string, unknown>
    ? KeysToCamelCase<T[K]>
    : T[K] extends Array<infer U>
      ? U extends Record<string, unknown>
        ? Array<KeysToCamelCase<U>>
        : T[K]
      : T[K]
}

export function toCamelCase<T>(obj: T): KeysToCamelCase<T> {
  if (obj === null || typeof obj !== 'object') {
    return obj as KeysToCamelCase<T>
  }

  if (Array.isArray(obj)) {
    return obj.map((item) => toCamelCase(item)) as KeysToCamelCase<T>
  }

  const result: Record<string, unknown> = {}

  for (const [key, value] of Object.entries(obj)) {
    const camelKey = key.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase())
    result[camelKey] = toCamelCase(value)
  }

  return result as KeysToCamelCase<T>
}
