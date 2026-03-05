import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { loginApi } from '../api/auth'
import { useAuth } from '../context/AuthContext'

function LogoMark() {
  return (
    <div className="relative flex items-center justify-center w-16 h-16 mx-auto mb-5">
      {/* Ping ring */}
      <span className="ping-slow absolute inline-flex w-16 h-16 rounded-full bg-accent/20" />
      {/* Outer ring */}
      <div className="absolute w-16 h-16 rounded-full border border-accent/30" />
      {/* Inner ring */}
      <div className="absolute w-10 h-10 rounded-full border border-accent/50" />
      {/* SVG icon */}
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor"
        strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round"
        className="text-accent relative z-10">
        <circle cx="12" cy="12" r="3" />
        <path d="M12 2v4M12 18v4M2 12h4M18 12h4" />
        <path d="M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M19.07 4.93l-2.83 2.83M7.76 16.24l-2.83 2.83" />
      </svg>
    </div>
  )
}

export function Login() {
  const navigate = useNavigate()
  const { setTokens, user } = useAuth()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  if (user) {
    navigate('/dashboard', { replace: true })
    return null
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const tokens = await loginApi(email, password)
      await setTokens(tokens.access_token, tokens.refresh_token)
      navigate('/dashboard', { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="auth-bg min-h-screen flex items-center justify-center p-6">
      <div className="w-full max-w-[380px]">

        {/* Logo + title */}
        <div className="text-center" style={{ marginBottom: '2rem' }}>
          <LogoMark />
          <h1 className="text-[1.6rem] font-bold tracking-tight text-white leading-tight">
            RoboControl
          </h1>
        </div>

        {/* Card - extra top padding for space before Operator Login */}
        <div className="auth-card rounded-2xl" style={{ paddingTop: '2rem', paddingBottom: '1.75rem', paddingLeft: '2.5rem', paddingRight: '2.5rem' }}>

          {/* Divider label */}
          <div className="flex items-center gap-3 mb-7">
            <div className="flex-1 h-px bg-border/60" />
            <span className="text-[10px] tracking-[0.15em] uppercase text-muted/60">
              Operator Login
            </span>
            <div className="flex-1 h-px bg-border/60" />
          </div>

          <form onSubmit={handleSubmit} className="flex flex-col gap-6" style={{ paddingBottom: '1.25rem' }}>

            {/* Email */}
            <div className="flex flex-col gap-1.5">
              <label htmlFor="email" className="flex items-center gap-1.5 text-xs font-semibold tracking-wider uppercase text-muted/80">
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="opacity-60">
                  <rect x="2" y="4" width="20" height="16" rx="2"/>
                  <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
                </svg>
                Email
              </label>
              <input
                id="email"
                type="email"
                placeholder="operator@mission.ctrl"
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="auth-input w-full px-4 py-3.5 rounded-xl text-sm font-mono tracking-wide"
                required
              />
            </div>

            {/* Password */}
            <div className="flex flex-col gap-1.5">
              <label htmlFor="password" className="flex items-center gap-1.5 text-xs font-semibold tracking-wider uppercase text-muted/80">
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="opacity-60">
                  <rect x="3" y="11" width="18" height="11" rx="2"/>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                </svg>
                Password
              </label>
              <input
                id="password"
                type="password"
                placeholder="••••••••••••"
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="auth-input w-full px-4 py-3.5 rounded-xl text-sm"
                required
              />
            </div>

            {/* Error */}
            {error && (
              <div className="flex items-start gap-2.5 text-sm text-danger bg-danger/8 border border-danger/20 rounded-xl px-4 py-3">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mt-px flex-shrink-0">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="12" x2="12" y1="8" y2="12"/>
                  <line x1="12" x2="12.01" y1="16" y2="16"/>
                </svg>
                {error}
              </div>
            )}

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className="auth-btn-primary mt-3 w-full py-5 rounded-xl text-white text-sm font-bold tracking-wide disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
                  </svg>
                  Authenticating…
                </span>
              ) : 'Login'}
            </button>
          </form>
        </div>

        {/* Footer */}
        <p className="text-center text-muted/70 text-xs tracking-wide" style={{ marginTop: '1.5rem' }}>
          No account?{' '}
          <Link to="/register" className="text-accent font-semibold hover:text-accent/80 transition-colors">
            Register as operator
          </Link>
        </p>

        {/* Bottom watermark */}
        <p className="text-center mt-8 text-[10px] tracking-[0.2em] uppercase text-muted/25">
          CMP9134 · Mission Control v1.0
        </p>
      </div>
    </main>
  )
}
