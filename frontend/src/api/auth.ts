import axios from 'axios'
import { api } from './client'

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

export async function loginApi(email: string, password: string): Promise<TokenData> {
  const res = await api.post<ApiResponse<TokenData>>('/auth/login', { email, password })
  return res.data
}

export async function registerApi(
  full_name: string,
  email: string,
  password: string,
): Promise<TokenData> {
  const res = await api.post<ApiResponse<TokenData>>('/auth/register', {
    full_name,
    email,
    password,
  })
  return res.data
}

export async function getSessionApi(): Promise<SessionData> {
  const res = await api.get<ApiResponse<SessionData>>('/auth/session')
  return res.data
}

export async function refreshTokenApi(): Promise<TokenData> {
  const refreshToken = localStorage.getItem('refresh_token')
  if (!refreshToken) throw new Error('No refresh token')
  const res = await api.post<ApiResponse<TokenData>>('/auth/refresh-token', {})
  return res.data
}

export async function logoutApi(): Promise<void> {
  const accessToken = localStorage.getItem('access_token')
  const refreshToken = localStorage.getItem('refresh_token') ?? ''
  await axios.post(
    '/v1/auth/logout',
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
