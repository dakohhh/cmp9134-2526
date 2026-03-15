import { api } from '../client'

export interface MapDataV1 {
  width: number
  height: number
  grid: number[][]
}

interface ApiResponse<T> {
  message: string
  data: T
  status_code: number
}

export async function getMapV1(): Promise<MapDataV1> {
  const res = await api.get<ApiResponse<MapDataV1>>(`/v1/map/?_=${Date.now()}`)
  const data = (res as ApiResponse<MapDataV1>).data
  if (!data?.grid || !Array.isArray(data.grid)) {
    throw new Error('Map data missing grid')
  }
  return data
}
