import { api } from './client'

export interface MapData {
  width: number
  height: number
  grid: number[][]
}

interface ApiResponse<T> {
  message: string
  data: T
  status_code: number
}

export async function getMapApi(): Promise<MapData> {
  const res = await api.get<ApiResponse<MapData>>(`/map/?_=${Date.now()}`)
  if (!res || typeof res !== 'object' || !('data' in res)) {
    throw new Error('Invalid map response')
  }
  const data = (res as ApiResponse<MapData>).data
  if (!data?.grid || !Array.isArray(data.grid)) {
    throw new Error('Map data missing grid')
  }
  return data
}
