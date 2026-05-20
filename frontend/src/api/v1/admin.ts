import { api } from '../client'

export interface UserEntryV1 {
  id: string
  full_name: string | null
  email: string
  role: string
}

export interface UsersMetaV1 {
  total: number
  per_page: number
  last_page: number
  current_page: number
  prev: number | null
  next: number | null
}

export interface UsersDataV1 {
  results: UserEntryV1[]
  meta: UsersMetaV1
}

interface ApiResponse<T> {
  message: string
  data: T
  status_code: number
}

export async function getAllUsersV1(page = 1, limit = 10): Promise<UsersDataV1> {
  const res = await api.get<ApiResponse<UsersDataV1>>(
    `/v1/admin/users/?page=${page}&limit=${limit}`,
  )
  return (res as ApiResponse<UsersDataV1>).data
}

export async function updateUserRoleV1(userId: string, role: string): Promise<void> {
  await api.post(`/v1/admin/user/${userId}/role`, { role })
}
