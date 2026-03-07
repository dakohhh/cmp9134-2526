import { useCallback, useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { getMapApi, type MapData } from '../api/map'
import { useRobotTelemetry } from '../hooks/useRobotTelemetry'

// Fallback grid size when no map data
const DEFAULT_SIZE = 21

function cellClass(
  value: number,
  x: number,
  y: number,
  robotX: number,
  robotY: number,
): string {
  const base = 'border border-[rgba(42,45,62,0.5)] flex items-center justify-center text-[clamp(6px,1.5vw,14px)]'
  if (x === robotX && y === robotY) return `${base} bg-accent text-white`
  if (value === 1) return `${base} bg-[rgba(255,71,87,0.25)]` // obstacle
  return base
}

export function Dashboard() {
  const { user, logout } = useAuth()
  const { telemetry } = useRobotTelemetry()
  const [mapData, setMapData] = useState<MapData | null>(null)
  const [mapError, setMapError] = useState<string | null>(null)
  const [mapLoading, setMapLoading] = useState(true)

  const fetchMap = useCallback(() => {
    setMapLoading(true)
    setMapError(null)
    getMapApi()
      .then(setMapData)
      .catch((err) => setMapError(err instanceof Error ? err.message : 'Failed to load map'))
      .finally(() => setMapLoading(false))
  }, [])

  useEffect(() => {
    fetchMap()
  }, [fetchMap])

  useEffect(() => {
    const onFocus = () => fetchMap()
    window.addEventListener('focus', onFocus)
    return () => window.removeEventListener('focus', onFocus)
  }, [fetchMap])

  const width = mapData?.width ?? DEFAULT_SIZE
  const height = mapData?.height ?? DEFAULT_SIZE
  const grid = mapData?.grid ?? []
  const robotX = telemetry?.position?.x ?? 0
  const robotY = telemetry?.position?.y ?? 0

  const cells = Array.from({ length: width * height }, (_, i) => {
    const x = i % width
    const y = Math.floor(i / width)
    const value = grid[y]?.[x] ?? 0
    return (
      <div key={i} className={cellClass(value, x, y, robotX, robotY)}>
        {x === robotX && y === robotY ? '▲' : null}
      </div>
    )
  })

  return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-6 p-6 pt-[4.5rem]">
      <header className="fixed top-0 left-0 right-0 h-14 flex items-center justify-between gap-5 px-6 bg-card/95 backdrop-blur-sm border-b border-white/5">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/[0.04] border border-white/10">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-muted flex-shrink-0">
              <rect x="2" y="7" width="18" height="10" rx="2" ry="2" />
              <line x1="22" y1="11" x2="22" y2="13" />
            </svg>
            <span className="text-sm font-medium text-white">
              {telemetry?.battery != null ? `${telemetry.battery}%` : '—'}
            </span>
            <span className="text-[10px] text-muted uppercase">Battery</span>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right">
            <p className="text-sm font-medium text-white">{user?.full_name ?? 'User'}</p>
            <p className="text-xs text-muted">{user?.email}</p>
          </div>
          <span className="text-[10px] uppercase tracking-widest px-3 py-1.5 rounded-full bg-accent/10 text-accent/90 font-semibold border border-accent/20">
            {user?.role ?? 'viewer'}
          </span>
        </div>
        <button
          type="button"
          className="py-2.5 px-5 text-sm font-medium text-muted bg-white/[0.04] border border-white/10 rounded-lg cursor-pointer transition-all hover:bg-[rgba(255,71,87,0.12)] hover:text-danger hover:border-danger/30"
          onClick={() => logout()}
        >
          Logout
        </button>
      </header>
      <div className="w-[min(80vh,560px)] h-[min(80vh,560px)]">
        <div className="flex items-center justify-between gap-4 mb-2">
          {mapError && (
            <p className="text-sm text-danger">{mapError}</p>
          )}
          <button
            type="button"
            onClick={fetchMap}
            disabled={mapLoading}
            className="text-xs text-muted hover:text-accent transition-colors disabled:opacity-50 ml-auto"
          >
            {mapLoading ? 'Loading…' : 'Refresh map'}
          </button>
        </div>
        <div
          className="grid w-full h-full border border-border rounded-[var(--radius)] overflow-hidden bg-card"
          style={{
            gridTemplateColumns: `repeat(${width}, 1fr)`,
            gridTemplateRows: `repeat(${height}, 1fr)`,
          }}
        >
          {cells}
        </div>
      </div>

      <div className="flex flex-col items-center gap-2.5">
        <span className="text-xs text-muted uppercase tracking-wider font-medium">Navigation Controls</span>
        <div className="grid grid-cols-3 grid-rows-3 gap-1.5 w-[156px]">
          <span className="invisible pointer-events-none" />
          <button
            type="button"
            className="w-12 h-12 rounded-[10px] border border-border bg-card text-accent text-xl flex items-center justify-center cursor-pointer transition-colors hover:bg-accent/20 hover:border-accent"
            aria-label="North"
          >
            ↑
          </button>
          <span className="invisible pointer-events-none" />

          <button
            type="button"
            className="w-12 h-12 rounded-[10px] border border-border bg-card text-accent text-xl flex items-center justify-center cursor-pointer transition-colors hover:bg-accent/20 hover:border-accent"
            aria-label="West"
          >
            ←
          </button>
          <button
            type="button"
            className="w-12 h-12 rounded-[10px] border border-border bg-border text-muted text-[0.45rem] flex items-center justify-center cursor-default hover:bg-border hover:border-border"
            aria-label="Stop"
          >
            ●
          </button>
          <button
            type="button"
            className="w-12 h-12 rounded-[10px] border border-border bg-card text-accent text-xl flex items-center justify-center cursor-pointer transition-colors hover:bg-accent/20 hover:border-accent"
            aria-label="East"
          >
            →
          </button>

          <span className="invisible pointer-events-none" />
          <button
            type="button"
            className="w-12 h-12 rounded-[10px] border border-border bg-card text-accent text-xl flex items-center justify-center cursor-pointer transition-colors hover:bg-accent/20 hover:border-accent"
            aria-label="South"
          >
            ↓
          </button>
          <span className="invisible pointer-events-none" />
        </div>
      </div>
    </div>
  )
}
