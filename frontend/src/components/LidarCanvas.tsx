import { useEffect, useRef } from 'react'

interface LidarCanvasProps {
  lidar: number[]
  size?: number
}

const MAX_RANGE = 10
const SWEEP_DURATION_MS = 2500

export function LidarCanvas({ lidar, size = 220 }: LidarCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const sweepAngleRef = useRef(0)
  const animationFrameRef = useRef<number>(0)
  const lastTimeRef = useRef<number>(0)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const center = size / 2
    const scale = (size / 2 - 20) / MAX_RANGE

    function draw(timestamp: number) {
      if (!ctx) return

      const delta = timestamp - lastTimeRef.current
      lastTimeRef.current = timestamp
      sweepAngleRef.current = (sweepAngleRef.current + (delta / SWEEP_DURATION_MS) * 360) % 360

      ctx.fillStyle = '#0f1117'
      ctx.fillRect(0, 0, size, size)

      ctx.strokeStyle = 'rgba(108, 99, 255, 0.15)'
      ctx.lineWidth = 1
      for (let r = 2; r <= 8; r += 2) {
        ctx.beginPath()
        ctx.arc(center, center, r * scale, 0, Math.PI * 2)
        ctx.stroke()
      }

      ctx.fillStyle = 'rgba(139, 143, 168, 0.5)'
      ctx.font = '9px Inter, sans-serif'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      ctx.fillText('N', center, 10)
      ctx.fillText('S', center, size - 10)
      ctx.fillText('W', 10, center)
      ctx.fillText('E', size - 10, center)

      ctx.fillStyle = '#6c63ff'
      ctx.beginPath()
      ctx.arc(center, center, 5, 0, Math.PI * 2)
      ctx.fill()

      const sweepRad = (sweepAngleRef.current * Math.PI) / 180
      ctx.strokeStyle = 'rgba(108, 99, 255, 0.6)'
      ctx.lineWidth = 2
      ctx.beginPath()
      ctx.moveTo(center, center)
      ctx.lineTo(
        center + Math.sin(sweepRad) * (size / 2 - 15),
        center - Math.cos(sweepRad) * (size / 2 - 15)
      )
      ctx.stroke()

      ctx.fillStyle = '#ff4757'
      for (let deg = 0; deg < lidar.length && deg < 360; deg++) {
        const dist = lidar[deg]
        if (dist < MAX_RANGE) {
          const angleRad = (deg * Math.PI) / 180
          const obsX = center + dist * Math.sin(angleRad) * scale
          const obsY = center - dist * Math.cos(angleRad) * scale
          ctx.beginPath()
          ctx.arc(obsX, obsY, 2, 0, Math.PI * 2)
          ctx.fill()
        }
      }

      animationFrameRef.current = requestAnimationFrame(draw)
    }

    lastTimeRef.current = performance.now()
    animationFrameRef.current = requestAnimationFrame(draw)

    return () => {
      cancelAnimationFrame(animationFrameRef.current)
    }
  }, [lidar, size])

  return (
    <canvas
      ref={canvasRef}
      width={size}
      height={size}
      className="rounded-lg border border-white/10"
      style={{ background: '#0f1117' }}
    />
  )
}
