export interface TelemetryPosition {
  x: number
  y: number
}

export interface TelemetrySensors {
  N: number
  S: number
  E: number
  W: number
  lidar: number[]
}

export interface TelemetryData {
  position: TelemetryPosition
  battery: number
  status: 'IDLE' | 'MOVING' | 'LOW_BATTERY' | 'STUCK'
  sensors: TelemetrySensors
}
