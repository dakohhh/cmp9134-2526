import { api } from '../client'

export interface AuditLogEntryV1 {
  id: string
  created_at: string
  updated_at: string
  user_id: string
  action: string
  navigation_direction: string | null
}

export interface AuditLogMetaV1 {
  total: number
  per_page: number
  last_page: number
  current_page: number
  prev: number | null
  next: number | null
}

export interface AuditLogDataV1 {
  results: AuditLogEntryV1[]
  meta: AuditLogMetaV1
}

interface ApiResponse<T> {
  message: string
  data: T
  status_code: number
}

export interface GetAuditLogsParamsV1 {
  page?: number
  limit?: number
}

export async function getAuditLogsV1(
  params: GetAuditLogsParamsV1 = {},
): Promise<AuditLogDataV1> {
  const { page = 1, limit = 10 } = params
  const res = await api.get<ApiResponse<AuditLogDataV1>>(
    `/v1/audit-log/?page=${page}&limit=${limit}`,
  )
  return (res as ApiResponse<AuditLogDataV1>).data
}
