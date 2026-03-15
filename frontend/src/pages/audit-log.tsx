import { useCallback, useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { getAuditLogsV1, type AuditLogDataV1, type AuditLogEntryV1 } from '../api/v1'

const PER_PAGE = 10

export function AuditLog() {
  const navigate = useNavigate()
  const { user, logout } = useAuth()
  const [data, setData] = useState<AuditLogDataV1 | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)

  const isCommander = user?.role?.toLowerCase() === 'commander'

  const fetchLogs = useCallback(async (p: number) => {
    setLoading(true)
    setError(null)
    try {
      const result = await getAuditLogsV1({ page: p, limit: PER_PAGE })
      setData(result)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load audit logs')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    if (!isCommander) {
      navigate('/dashboard', { replace: true })
      return
    }
    fetchLogs(page)
  }, [isCommander, navigate, page, fetchLogs])

  if (!isCommander) return null

  const meta = data?.meta
  const results = data?.results ?? []

  return (
    <div className="min-h-screen flex flex-col bg-bg">
      <header className="fixed top-0 left-0 right-0 z-10 h-14 flex items-center justify-between gap-5 px-6 bg-card/95 backdrop-blur-sm border-b border-white/5">
        <div className="flex items-center gap-4">
          <Link
            to="/dashboard"
            className="text-sm font-medium text-muted hover:text-white transition-colors"
          >
            Dashboard
          </Link>
          <span className="text-muted">·</span>
          <span className="text-sm font-medium text-white">Audit log</span>
        </div>
        <div className="flex items-center gap-4">
          <p className="text-sm font-medium text-white">{user?.full_name ?? 'User'}</p>
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

      <main className="flex-1 px-6 pb-6 w-full flex flex-col items-center" style={{ marginTop: '6rem' }}>
        <div className="w-full max-w-4xl">
        <h1 className="text-xl font-bold text-white mb-4">Audit logs</h1>

        {error && (
          <p className="text-sm text-danger bg-danger/10 border border-danger/20 rounded-lg px-3 py-2 mb-4">
            {error}
          </p>
        )}

        {loading ? (
          <p className="text-muted text-sm">Loading…</p>
        ) : (
          <>
            <div className="rounded-xl border border-white/10 bg-card/50 overflow-hidden">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-white/10 bg-white/[0.04]">
                    <th className="px-4 py-3 text-[10px] uppercase tracking-wider text-muted font-semibold">Time</th>
                    <th className="px-4 py-3 text-[10px] uppercase tracking-wider text-muted font-semibold">Action</th>
                    <th className="px-4 py-3 text-[10px] uppercase tracking-wider text-muted font-semibold">Direction</th>
                    <th className="px-4 py-3 text-[10px] uppercase tracking-wider text-muted font-semibold">User ID</th>
                  </tr>
                </thead>
                <tbody>
                  {results.map((entry: AuditLogEntryV1) => (
                    <tr key={entry.id} className="border-b border-white/5 hover:bg-white/[0.03]">
                      <td className="px-4 py-3 text-white font-mono text-xs">{entry.created_at}</td>
                      <td className="px-4 py-3 text-white">{entry.action}</td>
                      <td className="px-4 py-3 text-muted">{entry.navigation_direction ?? '—'}</td>
                      <td className="px-4 py-3 text-muted font-mono text-xs truncate max-w-[120px]" title={entry.user_id}>
                        {entry.user_id.slice(0, 8)}…
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {meta && (meta.last_page > 1 || meta.current_page > 1) && (
              <div className="flex items-center justify-between mt-4">
                <p className="text-xs text-muted">
                  Page {meta.current_page} of {meta.last_page} · {meta.total} total
                </p>
                <div className="flex gap-2">
                  <button
                    type="button"
                    disabled={meta.prev == null}
                    onClick={() => setPage((p) => p - 1)}
                    className="px-3 py-1.5 text-xs font-medium rounded-lg border border-white/10 bg-white/[0.04] text-white disabled:opacity-40 disabled:cursor-not-allowed hover:bg-white/[0.08]"
                  >
                    Previous
                  </button>
                  <button
                    type="button"
                    disabled={meta.next == null}
                    onClick={() => setPage((p) => p + 1)}
                    className="px-3 py-1.5 text-xs font-medium rounded-lg border border-white/10 bg-white/[0.04] text-white disabled:opacity-40 disabled:cursor-not-allowed hover:bg-white/[0.08]"
                  >
                    Next
                  </button>
                </div>
              </div>
            )}
          </>
        )}
        </div>
      </main>
    </div>
  )
}
