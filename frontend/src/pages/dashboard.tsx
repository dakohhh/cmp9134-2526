import { useAuth } from '../context/AuthContext'

const GRID_SIZE = 21

// (x, y) → flat index (y=0 is top row)
function cellIndex(x: number, y: number) {
  return y * GRID_SIZE + x
}

// Robot starts at (0,0); charging station is at (0,0)
const ROBOT_X = 0
const ROBOT_Y = 0
const ROBOT_IDX = cellIndex(ROBOT_X, ROBOT_Y)
const CHARGE_IDX = cellIndex(0, 0)

function cellClass(idx: number): string {
  const base = 'border border-[rgba(42,45,62,0.5)] flex items-center justify-center text-[clamp(6px,1.5vw,14px)]'
  if (idx === ROBOT_IDX) return `${base} bg-accent text-white`
  if (idx === CHARGE_IDX) return `${base} bg-[rgba(0,200,150,0.2)]`
  return base
}

export function Dashboard() {
  const { user, logout } = useAuth()

  const cells = Array.from({ length: GRID_SIZE * GRID_SIZE }, (_, i) => (
    <div key={i} className={cellClass(i)}>
      {i === ROBOT_IDX ? '▲' : null}
    </div>
  ))

  return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-6 p-6 pt-[4.5rem]">
      <header className="fixed top-0 left-0 right-0 h-14 flex items-center justify-end gap-4 px-6 bg-card border-b border-border">
        <div className="flex items-center gap-4 mr-2">
          <div className="text-right">
            <p className="text-sm font-medium text-white">{user?.full_name ?? 'User'}</p>
            <p className="text-xs text-muted">{user?.email}</p>
          </div>
          <span className="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded bg-accent/20 text-accent font-medium">
            {user?.role ?? 'viewer'}
          </span>
        </div>
        <button
          type="button"
          className="py-1.5 px-4 text-sm bg-card text-muted border border-border rounded-[var(--radius)] cursor-pointer transition-colors hover:bg-[rgba(255,71,87,0.15)] hover:text-danger hover:border-[rgba(255,71,87,0.3)]"
          onClick={() => logout()}
        >
          Logout
        </button>
      </header>
      <div className="w-[min(80vh,560px)] h-[min(80vh,560px)]">
        <div className="grid grid-cols-[repeat(21,1fr)] grid-rows-[repeat(21,1fr)] w-full h-full border border-border rounded-[var(--radius)] overflow-hidden bg-card">
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
