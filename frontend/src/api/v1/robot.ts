import { api } from '../client'

export const NavigationEnumV1 = {
  LEFT: 'LEFT',
  RIGHT: 'RIGHT',
  UP: 'UP',
  DOWN: 'DOWN',
} as const

export type NavigationV1 = (typeof NavigationEnumV1)[keyof typeof NavigationEnumV1]

export interface MoveRobotRequestV1 {
  navigation: NavigationV1
}

interface MoveRobotResponseV1 {
  message: string
  data: null
  status_code: number
}

export async function moveRobotV1(navigation: NavigationV1): Promise<void> {
  const body: MoveRobotRequestV1 = { navigation }
  await api.post<MoveRobotResponseV1>('/v1/robot/move/', body)
}

export async function resetRobotV1(): Promise<void> {
  await api.post<MoveRobotResponseV1>('/v1/robot/reset/', {})
}
