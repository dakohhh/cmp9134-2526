import { useEffect, useState } from 'react'

export interface TelemetryData {
  position: { x: number; y: number }
  battery: number
  status: string
}

export function useRobotTelemetry() {
  const [telemetry, setTelemetry] = useState<TelemetryData | null>(null)
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    const wsUrl = `${protocol}//${host}/v1/robot/`

    const ws = new WebSocket(wsUrl)

    ws.onopen = () => setConnected(true)
    ws.onclose = () => setConnected(false)
    ws.onerror = () => setConnected(false)

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data)
        if (msg?.type === 'TELEMETRY' && msg?.data) {
          setTelemetry(msg.data)
        }
      } catch {
        // ignore parse errors
      }
    }

    return () => {
      ws.close()
    }
  }, [])

  return { telemetry, connected }
}
