import {
  createContext,
  useContext,
  useState,
  useCallback,
  useEffect,
  type ReactNode,
} from 'react'
import { getSessionApi, logoutApi } from '../api/auth'

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
      await logoutApi()
    } catch {
      // proceed with local cleanup even if the API call fails
    }
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setUser(null)
  }, [])

  const setTokens = useCallback(
    async (accessToken: string, refreshToken: string) => {
      localStorage.setItem('access_token', accessToken)
      localStorage.setItem('refresh_token', refreshToken)
      try {
        const data = await getSessionApi()
        setUser({ full_name: data.full_name, email: data.email, role: data.role })
      } catch {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        setUser(null)
        throw new Error('Failed to load session')
      }
    },
    [],
  )

  // On mount, try to restore session from stored token
  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      setIsLoading(false)
      return
    }

    getSessionApi()
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
