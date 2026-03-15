import {
  createContext,
  useContext,
  useState,
  useCallback,
  useEffect,
  type ReactNode,
} from 'react'
import { getSessionV1, logoutV1 } from '../api/v1'
import { accessTokenCookie } from '../utils/cookies'

interface AuthUser {
  full_name: string
  email: string
  role: 'viewer' | 'commander'
}

interface AuthContextValue {
  user: AuthUser | null
  isLoading: boolean
  isAuthenticated: boolean
  setTokens: (accessToken: string, refreshToken: string) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const logout = useCallback(async () => {
    try {
      await logoutV1()
    } catch {
      // proceed with local cleanup even if the API call fails
    }
    accessTokenCookie.remove()
    localStorage.removeItem('refresh_token')
    setUser(null)
  }, [])

  const setTokens = useCallback(
    async (accessToken: string, refreshToken: string) => {
      accessTokenCookie.set(accessToken)
      localStorage.setItem('refresh_token', refreshToken)
      try {
        const data = await getSessionV1()
        setUser({ full_name: data.full_name, email: data.email, role: data.role })
      } catch {
        accessTokenCookie.remove()
        localStorage.removeItem('refresh_token')
        setUser(null)
        throw new Error('Failed to load session')
      }
    },
    [],
  )

  // On mount, try to restore session from stored token
  useEffect(() => {
    const token = accessTokenCookie.get()
    if (!token) {
      setIsLoading(false)
      return
    }

    getSessionV1()
      .then((data) => setUser({ full_name: data.full_name, email: data.email, role: data.role }))
      .catch(() => logout())
      .finally(() => setIsLoading(false))
  }, [logout])

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: user !== null,
        setTokens,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
