import { useCallback, useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { Link } from 'react-router-dom'
import {
  getMapV1,
  moveRobotV1,
  resetRobotV1,
  NavigationEnumV1,
  type MapDataV1,
  type NavigationV1,
} from '../api/v1'
import { useRobotTelemetry } from '../hooks/useRobotTelemetry'
import { LidarCanvas } from '../components/LidarCanvas'

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
  const [mapData, setMapData] = useState<MapDataV1 | null>(null)
  const [mapError, setMapError] = useState<string | null>(null)
  const [mapLoading, setMapLoading] = useState(true)
  const [moveLoading, setMoveLoading] = useState(false)
  const [moveError, setMoveError] = useState<string | null>(null)
  const [resetLoading, setResetLoading] = useState(false)
  const [resetError, setResetError] = useState<string | null>(null)

  const canMove = user?.role?.toLowerCase() === 'commander'

  const handleMove = useCallback(
    async (navigation: NavigationV1) => {
      if (!canMove) return
      setMoveError(null)
      setMoveLoading(true)
      try {
        await moveRobotV1(navigation)
      } catch (err) {
        setMoveError(err instanceof Error ? err.message : 'Failed to move robot')
      } finally {
        setMoveLoading(false)
      }
    },
    [canMove],
  )

  const fetchMap = useCallback(() => {
    setMapLoading(true)
    setMapError(null)
    getMapV1()
      .then(setMapData)
      .catch((err) => setMapError(err instanceof Error ? err.message : 'Failed to load map'))
      .finally(() => setMapLoading(false))
  }, [])

  const handleReset = useCallback(async () => {
    if (!canMove) return
    setResetError(null)
    setResetLoading(true)
    try {
      await resetRobotV1()
      fetchMap()
    } catch (err) {
      setResetError(err instanceof Error ? err.message : 'Failed to reset robot')
    } finally {
      setResetLoading(false)
    }
  }, [canMove, fetchMap])

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

  const sensors = telemetry?.sensors
  const hasSensors = sensors != null

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
    <div className="min-h-screen flex flex-col bg-bg">
      <header className="fixed top-0 left-0 right-0 z-10 h-14 flex items-center justify-between gap-5 px-6 bg-card/95 backdrop-blur-sm border-b border-white/5">
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
          <div
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border ${
              telemetry?.status === 'LOW_BATTERY' || telemetry?.status === 'STUCK'
                ? 'bg-danger/10 border-danger/30 text-danger'
                : 'bg-white/[0.04] border-white/10 text-muted'
            }`}
          >
            <span className="text-[10px] uppercase tracking-wider font-semibold">
              {telemetry?.status ?? '—'}
            </span>
            <span className="text-[10px] text-muted uppercase">Status</span>
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
          {canMove && (
            <Link
              to="/audit-log"
              className="text-sm font-medium text-muted hover:text-accent transition-colors"
            >
              Audit log
            </Link>
          )}
        </div>
        <button
          type="button"
          className="py-2.5 px-5 text-sm font-medium text-muted bg-white/[0.04] border border-white/10 rounded-lg cursor-pointer transition-all hover:bg-[rgba(255,71,87,0.12)] hover:text-danger hover:border-danger/30"
          onClick={() => logout()}
        >
          Logout
        </button>
      </header>
      <div className="flex flex-1 flex-nowrap gap-8 items-start justify-center px-6 pb-6" style={{ marginTop: '5rem' }}>
        <aside className="dashboard-left flex flex-col gap-5 w-52 flex-shrink-0 rounded-xl border border-white/10 bg-card/50 p-4 mt-2">
          <section>
            <h2 className="dashboard-section-title text-[11px] font-semibold tracking-widest uppercase text-muted/90 mb-3">
              Sensors
            </h2>
            <div className="flex flex-col gap-3">
              <div
                className="grid gap-1.5"
                style={{
                  gridTemplateColumns: '1fr 1fr 1fr',
                  gridTemplateRows: 'auto auto auto',
                }}
              >
                <span className="invisible h-0 overflow-hidden" aria-hidden>placeholder</span>
                <div className="flex flex-col items-center justify-center rounded-lg border border-white/10 bg-white/[0.06] px-2 py-2.5 min-h-[52px]">
                  <span className="text-[10px] uppercase tracking-wider text-muted/90">N</span>
                  <span className="text-white font-mono text-sm tabular-nums mt-0.5">{hasSensors && sensors?.N != null ? `${sensors.N}u` : '—'}</span>
                </div>
                <span className="invisible h-0 overflow-hidden" aria-hidden>placeholder</span>
                <div className="flex flex-col items-center justify-center rounded-lg border border-white/10 bg-white/[0.06] px-2 py-2.5 min-h-[52px]">
                  <span className="text-[10px] uppercase tracking-wider text-muted/90">W</span>
                  <span className="text-white font-mono text-sm tabular-nums mt-0.5">{hasSensors && sensors?.W != null ? `${sensors.W}u` : '—'}</span>
                </div>
                <div className="rounded-lg border border-white/5 bg-white/[0.02] min-h-[52px]" aria-hidden />
                <div className="flex flex-col items-center justify-center rounded-lg border border-white/10 bg-white/[0.06] px-2 py-2.5 min-h-[52px]">
                  <span className="text-[10px] uppercase tracking-wider text-muted/90">E</span>
                  <span className="text-white font-mono text-sm tabular-nums mt-0.5">{hasSensors && sensors?.E != null ? `${sensors.E}u` : '—'}</span>
                </div>
                <span className="invisible h-0 overflow-hidden" aria-hidden>placeholder</span>
                <div className="flex flex-col items-center justify-center rounded-lg border border-white/10 bg-white/[0.06] px-2 py-2.5 min-h-[52px]">
                  <span className="text-[10px] uppercase tracking-wider text-muted/90">S</span>
                  <span className="text-white font-mono text-sm tabular-nums mt-0.5">{hasSensors && sensors?.S != null ? `${sensors.S}u` : '—'}</span>
                </div>
                <span className="invisible h-0 overflow-hidden" aria-hidden>placeholder</span>
              </div>
              <div className="rounded-lg border border-white/10 bg-white/[0.06] px-3 py-2 text-center">
                <span className="text-xs text-muted/90">360° Scan: </span>
                <span className="text-xs text-white font-medium">{hasSensors && Array.isArray(sensors?.lidar) && sensors.lidar.length > 0 ? 'active' : '—'}</span>
              </div>
              {hasSensors && Array.isArray(sensors?.lidar) && sensors.lidar.length > 0 && (
                <div className="mt-2">
                  <LidarCanvas lidar={sensors.lidar} size={200} />
                </div>
              )}
            </div>
          </section>
        </aside>
        <div className="flex flex-col items-center gap-6 flex-shrink-0">
          <div className="w-[min(80vh,560px)] h-[min(80vh,560px)]">
            <div className="flex items-center justify-between gap-4 mb-2">
              <div className="flex items-center gap-2 flex-wrap min-w-0">
                {mapError && (
                  <span className="text-xs text-danger bg-danger/10 border border-danger/20 rounded-lg px-3 py-1.5">{mapError}</span>
                )}
                {resetError && (
                  <span className="text-xs text-danger bg-danger/10 border border-danger/20 rounded-lg px-3 py-1.5">{resetError}</span>
                )}
              </div>
          <div className="flex items-center gap-3 ml-auto">
            {canMove && (
              <button
                type="button"
                onClick={handleReset}
                disabled={resetLoading}
                className="text-xs text-muted hover:text-accent transition-colors disabled:opacity-50 py-1.5 px-3 rounded-lg border border-white/10 hover:border-accent/50"
              >
                {resetLoading ? 'Resetting…' : 'Restart robot'}
              </button>
            )}
            <button
              type="button"
              onClick={fetchMap}
              disabled={mapLoading}
              className="text-xs text-muted hover:text-accent transition-colors disabled:opacity-50"
            >
              {mapLoading ? 'Loading…' : 'Refresh map'}
            </button>
          </div>
        </div>
        <div
          className="grid w-full h-full border border-white/10 rounded-xl overflow-hidden bg-card shadow-lg"
          style={{
            gridTemplateColumns: `repeat(${width}, 1fr)`,
            gridTemplateRows: `repeat(${height}, 1fr)`,
          }}
        >
          {cells}
        </div>
      </div>

      {canMove && (
        <div className="flex flex-col items-center gap-3">
          {moveError && (
            <span className="text-xs text-danger bg-danger/10 border border-danger/20 rounded-lg px-3 py-1.5">{moveError}</span>
          )}
          <span className="text-[11px] text-muted uppercase tracking-widest font-medium">
            Navigation Controls
          </span>
          <div className="grid grid-cols-3 grid-rows-3 gap-1.5 w-[156px]">
            <span className="invisible pointer-events-none" />
            <button
              type="button"
              disabled={moveLoading}
              onClick={() => handleMove(NavigationEnumV1.UP)}
              className="w-12 h-12 rounded-[10px] border border-border bg-card text-accent text-xl flex items-center justify-center cursor-pointer transition-colors hover:bg-accent/20 hover:border-accent disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label="North"
            >
              ↑
            </button>
            <span className="invisible pointer-events-none" />

            <button
              type="button"
              disabled={moveLoading}
              onClick={() => handleMove(NavigationEnumV1.LEFT)}
              className="w-12 h-12 rounded-[10px] border border-border bg-card text-accent text-xl flex items-center justify-center cursor-pointer transition-colors hover:bg-accent/20 hover:border-accent disabled:opacity-50 disabled:cursor-not-allowed"
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
              disabled={moveLoading}
              onClick={() => handleMove(NavigationEnumV1.RIGHT)}
              className="w-12 h-12 rounded-[10px] border border-border bg-card text-accent text-xl flex items-center justify-center cursor-pointer transition-colors hover:bg-accent/20 hover:border-accent disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label="East"
            >
              →
            </button>

            <span className="invisible pointer-events-none" />
            <button
              type="button"
              disabled={moveLoading}
              onClick={() => handleMove(NavigationEnumV1.DOWN)}
              className="w-12 h-12 rounded-[10px] border border-border bg-card text-accent text-xl flex items-center justify-center cursor-pointer transition-colors hover:bg-accent/20 hover:border-accent disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label="South"
            >
              ↓
            </button>
            <span className="invisible pointer-events-none" />
          </div>
        </div>
      )}
        </div>
      </div>
    </div>
  )
}
