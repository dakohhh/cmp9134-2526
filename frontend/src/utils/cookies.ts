const ACCESS_TOKEN_KEY = 'access_token'

/** Default max-age: 7 days (in seconds) */
const DEFAULT_MAX_AGE = 7 * 24 * 60 * 60

function getCookie(name: string): string | null {
  if (typeof document === 'undefined') return null
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'))
  return match ? decodeURIComponent(match[2]) : null
}

function setCookie(
  name: string,
  value: string,
  options: { maxAge?: number; secure?: boolean; sameSite?: 'Lax' | 'Strict' | 'None' } = {},
): void {
  if (typeof document === 'undefined') return
  const { maxAge = DEFAULT_MAX_AGE, secure = false, sameSite = 'Lax' } = options
  let cookie = `${name}=${encodeURIComponent(value)}; path=/; max-age=${maxAge}; SameSite=${sameSite}`
  if (secure) cookie += '; Secure'
  document.cookie = cookie
}

function deleteCookie(name: string): void {
  if (typeof document === 'undefined') return
  document.cookie = `${name}=; path=/; max-age=0`
}

export const accessTokenCookie = {
  get(): string | null {
    return getCookie(ACCESS_TOKEN_KEY)
  },
  set(value: string, options?: { maxAge?: number; secure?: boolean; sameSite?: 'Lax' | 'Strict' | 'None' }): void {
    setCookie(ACCESS_TOKEN_KEY, value, options)
  },
  remove(): void {
    deleteCookie(ACCESS_TOKEN_KEY)
  },
}
