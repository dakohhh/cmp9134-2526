import axios from 'axios'
import { api } from '../client'
import { accessTokenCookie } from '../../utils/cookies'

export interface TokenData {
  access_token: string
  refresh_token: string
}

export type UserRole = 'viewer' | 'commander'

export interface SessionData {
  full_name: string
  email: string
  role: UserRole
}

interface ApiResponse<T> {
  message: string
  data: T
  status_code: number
}

export async function getSessionV1(): Promise<SessionData> {
  const res = await api.get<ApiResponse<SessionData>>('/v1/auth/session')
  return (res as ApiResponse<SessionData>).data
}

export async function loginV1(email: string, password: string): Promise<TokenData> {
  const res = await api.post<ApiResponse<TokenData>>('/v1/auth/login', { email, password })
  return (res as ApiResponse<TokenData>).data
}

export async function registerV1(
  full_name: string,
  email: string,
  password: string,
): Promise<TokenData> {
  const res = await api.post<ApiResponse<TokenData>>('/v1/auth/register', {
    full_name,
    email,
    password,
  })
  return (res as ApiResponse<TokenData>).data
}

export async function refreshTokenV1(): Promise<TokenData> {
  const refreshToken = localStorage.getItem('refresh_token')
  if (!refreshToken) throw new Error('No refresh token')
  const res = await api.post<ApiResponse<TokenData>>('/v1/auth/refresh-token', {})
  return (res as ApiResponse<TokenData>).data
}

export async function logoutV1(): Promise<void> {
  const accessToken = accessTokenCookie.get()
  const refreshToken = localStorage.getItem('refresh_token') ?? ''
  await axios.post(
    '/api/v1/auth/logout',
    {},
    {
      headers: {
        'Content-Type': 'application/json',
        ...(accessToken && { Authorization: `Bearer ${accessToken}` }),
        ...(refreshToken && { Cookie: `refresh_token=${refreshToken}` }),
      },
    },
  )
}
