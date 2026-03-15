import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { registerV1 } from '../api/v1'
import { useAuth } from '../context/AuthContext'

function Field({
  id, label, type = 'text', placeholder, autoComplete, value, onChange, icon,
}: {
  id: string
  label: string
  type?: string
  placeholder: string
  autoComplete: string
  value: string
  onChange: (v: string) => void
  icon: React.ReactNode
}) {
  return (
    <div className="flex flex-col gap-1.5">
      <label htmlFor={id} className="flex items-center gap-1.5 text-xs font-semibold tracking-wider uppercase text-muted/80">
        {icon}
        {label}
      </label>
      <input
        id={id}
        type={type}
        placeholder={placeholder}
        autoComplete={autoComplete}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="auth-input w-full px-4 py-3.5 rounded-xl text-sm"
        required
      />
    </div>
  )
}

const iconUser = (
  <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="opacity-60">
    <circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/>
  </svg>
)
const iconEmail = (
  <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="opacity-60">
    <rect x="2" y="4" width="20" height="16" rx="2"/>
    <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
  </svg>
)
const iconLock = (
  <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="opacity-60">
    <rect x="3" y="11" width="18" height="11" rx="2"/>
    <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
  </svg>
)

export function Register() {
  const navigate = useNavigate()
  const { setTokens } = useAuth()

  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError('')

    if (password !== confirm) {
      setError('Passwords do not match')
      return
    }
    if (password.length < 8) {
      setError('Password must be at least 8 characters')
      return
    }

    setLoading(true)
    try {
      const tokens = await registerV1(fullName, email, password)
      await setTokens(tokens.access_token, tokens.refresh_token)
      navigate('/dashboard', { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="auth-bg min-h-screen flex items-center justify-center p-6">
      <div className="w-full max-w-[380px]">

        {/* Header */}
        <div className="text-center" style={{ marginBottom: '2rem' }}>
          <h1 className="text-[1.6rem] font-bold tracking-tight text-white leading-tight">
            RoboControl
          </h1>
        </div>

        {/* Card - extra top padding for space before form */}
        <div className="auth-card rounded-2xl" style={{ paddingTop: '2rem', paddingBottom: '1.75rem', paddingLeft: '2.5rem', paddingRight: '2.5rem' }}>

          <div className="flex items-center gap-3 mb-7">
            <div className="flex-1 h-px bg-border/60" />
            <span className="text-[10px] tracking-[0.15em] uppercase text-muted/60">
              New Operator
            </span>
            <div className="flex-1 h-px bg-border/60" />
          </div>

          <form onSubmit={handleSubmit} className="flex flex-col gap-5" style={{ paddingBottom: '1.25rem' }}>
            <Field id="fullName" label="Full Name" placeholder="Jane Smith"
              autoComplete="name" value={fullName} onChange={setFullName} icon={iconUser} />

            <Field id="email" label="Email" type="email" placeholder="operator@mission.ctrl"
              autoComplete="email" value={email} onChange={setEmail} icon={iconEmail} />

            <Field id="password" label="Password" type="password" placeholder="Min. 8 characters"
              autoComplete="new-password" value={password} onChange={setPassword} icon={iconLock} />

            <Field id="confirm" label="Confirm Password" type="password" placeholder="••••••••••••"
              autoComplete="new-password" value={confirm} onChange={setConfirm} icon={iconLock} />

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
                  Creating account…
                </span>
              ) : 'Create Account'}
            </button>
          </form>
        </div>

        <p className="text-center text-muted/70 text-xs tracking-wide" style={{ marginTop: '1.5rem' }}>
          Already registered?{' '}
          <Link to="/login" className="text-accent font-semibold hover:text-accent/80 transition-colors">
            Login
          </Link>
        </p>

        <p className="text-center mt-8 text-[10px] tracking-[0.2em] uppercase text-muted/25">
          CMP9134 · Mission Control v1.0
        </p>
      </div>
    </main>
  )
}
