import { useEffect, useRef, useState } from 'react'

const RECONNECT_DELAY_MS = 3000

export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected'

export interface TelemetrySensors {
  N: number
  S: number
  E: number
  W: number
  lidar: number[]
}

export interface TelemetryData {
  position: { x: number; y: number }
  battery: number
  status: string
  sensors?: TelemetrySensors
}

export function useRobotTelemetry() {
  const [telemetry, setTelemetry] = useState<TelemetryData | null>(null)
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('connecting')
  const cancelledRef = useRef(false)
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    cancelledRef.current = false
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    const wsUrl = `${protocol}//${host}/api/v1/robot/`

    function connect() {
      if (cancelledRef.current) return
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws

      ws.onopen = () => setConnectionStatus('connected')
      ws.onclose = () => {
        setConnectionStatus('disconnected')
        if (cancelledRef.current) return
        reconnectTimeoutRef.current = setTimeout(connect, RECONNECT_DELAY_MS)
      }
      ws.onerror = () => {
        setConnectionStatus('disconnected')
        ws.close()
      }

      ws.onmessage = (event) => {
        try {
          const raw = typeof event.data === 'string' ? event.data : ''
          const msg = raw ? JSON.parse(raw) : null
          if (!msg || typeof msg !== 'object') return

          const type = msg.type === 'TELEMETRY' || msg.type === 'telemetry' ? 'TELEMETRY' : msg.type

          if (type === 'TELEMETRY') {
            const d = msg.data
            if (d && typeof d === 'object') {
              const pos = d.position && typeof d.position === 'object' ? d.position : { x: 0, y: 0 }
              const num = (v: unknown) => (Number.isFinite(Number(v)) ? Number(v) : 0)
              
              let sensors: TelemetrySensors | undefined
              if (d.sensors && typeof d.sensors === 'object') {
                const s = d.sensors
                sensors = {
                  N: num(s.N),
                  S: num(s.S),
                  E: num(s.E),
                  W: num(s.W),
                  lidar: Array.isArray(s.lidar) ? s.lidar.map((v: unknown) => num(v)) : [],
                }
              }

              setTelemetry({
                position: { x: num(pos.x), y: num(pos.y) },
                battery: num(d.battery),
                status: typeof d.status === 'string' ? d.status : '',
                sensors,
              })
            }
            setConnectionStatus('connected')
          } else if (type === 'ERROR') {
            setConnectionStatus('disconnected')
          }
        } catch {
          // ignore parse errors
        }
      }
    }

    connect()

    return () => {
      cancelledRef.current = true
      if (reconnectTimeoutRef.current != null) {
        clearTimeout(reconnectTimeoutRef.current)
        reconnectTimeoutRef.current = null
      }
      if (wsRef.current != null) {
        wsRef.current.close()
        wsRef.current = null
      }
    }
  }, [])

  return { telemetry, connectionStatus }
}
