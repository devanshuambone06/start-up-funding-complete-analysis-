/**
 * Login.jsx — Production Authentication Page
 * Supports: Google OAuth, Mobile OTP, Email/Password Login, Sign Up, Forgot Password.
 */
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { fetchOverview } from '../services/api'
import {
  TrendingUp, BarChart2, Zap, Eye, EyeOff,
  ArrowLeft, CheckCircle, Mail, Shield,
} from 'lucide-react'

// ── Shared style tokens ───────────────────────────────────────────────────────
const inputCls =
  'w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-white outline-none focus:border-violet-500/60 transition-colors placeholder:text-slate-600'
const labelCls = 'block text-[11px] font-semibold tracking-wider text-slate-400 uppercase mb-1.5'
const primaryBtn =
  'w-full py-3 rounded-xl border-none bg-gradient-to-r from-violet-600 to-blue-600 text-white font-bold text-sm cursor-pointer hover:from-violet-500 hover:to-blue-500 transition-all duration-200 active:scale-[0.98] shadow-lg shadow-violet-900/20 disabled:opacity-50 disabled:cursor-not-allowed'

// Auth modes
const MODES = { LOGIN: 'login', SIGNUP: 'signup', FORGOT: 'forgot', FORGOT_SENT: 'forgot_sent' }

const FEATURES = [
  { icon: TrendingUp, label: 'Real-time funding trend analytics' },
  { icon: BarChart2, label: 'Sector-wise investment breakdown' },
  { icon: Zap, label: 'AI-powered startup success prediction' },
]

// ── Google Button ─────────────────────────────────────────────────────────────
function GoogleButton({ onClick, loading }) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={loading}
      className="w-full flex items-center justify-center gap-3 py-3.5 rounded-xl border border-slate-700 bg-slate-900 text-slate-200 text-sm font-semibold cursor-pointer hover:bg-slate-800 hover:border-slate-600 transition-all duration-200 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed shadow-md"
    >
      <svg width="18" height="18" viewBox="0 0 24 24">
        <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
        <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
        <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
        <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
      </svg>
      {loading ? 'Connecting…' : 'Continue with Google'}
    </button>
  )
}

// ── Error Box ─────────────────────────────────────────────────────────────────
function ErrorBox({ error }) {
  if (!error) return null
  return (
    <div className="bg-red-500/10 border border-red-500/30 rounded-xl px-4 py-3 text-sm text-red-400 mb-4">
      ⚠ {error}
    </div>
  )
}

// ── Success Box ───────────────────────────────────────────────────────────────
function SuccessBox({ msg }) {
  if (!msg) return null
  return (
    <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-xl px-4 py-3 text-sm text-emerald-400 mb-3">
      ✓ {msg}
    </div>
  )
}

// ── Google Account Chooser Modal ──────────────────────────────────────────────
function GoogleAccountModal({ onClose, onSelect }) {
  const [customMode, setCustomMode] = useState(false)
  const [customEmail, setCustomEmail] = useState('')
  const [customName, setCustomName] = useState('')
  const [err, setErr] = useState('')

  const accounts = [
    { name: 'Devanshu Ambone', email: 'devanshu.ambone@gmail.com', avatar: 'D', color: '#8b5cf6' },
    { name: 'Raju Analytics', email: 'raju.analytics@gmail.com', avatar: 'R', color: '#3b82f6' },
    { name: 'Athenura Admin', email: 'admin.user@athenura.in', avatar: 'A', color: '#10b981' },
    { name: 'Startup Investor', email: 'investor.demo@gmail.com', avatar: 'I', color: '#f59e0b' },
  ]

  const handleCustomSubmit = (e) => {
    e.preventDefault()
    if (!customEmail.includes('@')) {
      setErr('Please enter a valid Gmail / Email address.')
      return
    }
    onSelect({ name: customName.trim() || customEmail.split('@')[0], email: customEmail.trim() })
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fade-in">
      <div className="w-full max-w-md bg-slate-900 border border-slate-700/60 rounded-2xl p-6 shadow-2xl space-y-5">
        {/* Header */}
        <div className="text-center">
          <div className="w-12 h-12 rounded-full bg-slate-800 border border-slate-700 mx-auto flex items-center justify-center mb-3">
            <svg width="24" height="24" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
            </svg>
          </div>
          <h3 className="text-xl font-bold text-white">Choose a Google Account</h3>
          <p className="text-xs text-slate-400 mt-1">Select an account to sign in to Startup Analytics</p>
        </div>

        {err && <div className="bg-red-500/10 border border-red-500/30 rounded-xl px-3 py-2 text-xs text-red-400">{err}</div>}

        {!customMode ? (
          <div className="space-y-2">
            {accounts.map((acc) => (
              <button
                key={acc.email}
                type="button"
                onClick={() => onSelect(acc)}
                className="w-full flex items-center gap-3.5 p-3 rounded-xl border border-slate-800 bg-slate-950/60 hover:bg-slate-800/80 hover:border-slate-600 transition-all text-left group"
              >
                <div
                  className="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-sm shrink-0"
                  style={{ backgroundColor: acc.color }}
                >
                  {acc.avatar}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-white group-hover:text-violet-300 transition-colors truncate">{acc.name}</p>
                  <p className="text-xs text-slate-400 truncate">{acc.email}</p>
                </div>
              </button>
            ))}

            <button
              type="button"
              onClick={() => setCustomMode(true)}
              className="w-full flex items-center gap-3 p-3 rounded-xl border border-dashed border-slate-700 bg-transparent text-violet-400 hover:text-violet-300 hover:bg-violet-500/10 hover:border-violet-500/50 transition-all text-sm font-medium"
            >
              <span className="w-9 h-9 rounded-full bg-violet-500/20 flex items-center justify-center text-base">+</span>
              <span>Use another Gmail account</span>
            </button>
          </div>
        ) : (
          <form onSubmit={handleCustomSubmit} className="space-y-3.5">
            <div>
              <label className="block text-[11px] font-semibold text-slate-400 uppercase mb-1">Your Name</label>
              <input
                type="text"
                value={customName}
                onChange={(e) => setCustomName(e.target.value)}
                placeholder="e.g. Devanshu Ambone"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-white outline-none focus:border-violet-500"
              />
            </div>
            <div>
              <label className="block text-[11px] font-semibold text-slate-400 uppercase mb-1">Gmail / Email Address *</label>
              <input
                type="email"
                required
                value={customEmail}
                onChange={(e) => setCustomEmail(e.target.value)}
                placeholder="you@gmail.com"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-white outline-none focus:border-violet-500"
              />
            </div>
            <div className="flex gap-2 pt-2">
              <button
                type="button"
                onClick={() => setCustomMode(false)}
                className="flex-1 py-2.5 rounded-xl border border-slate-700 bg-slate-800 text-slate-300 text-xs font-semibold hover:bg-slate-700"
              >
                Back
              </button>
              <button
                type="submit"
                className="flex-1 py-2.5 rounded-xl bg-gradient-to-r from-violet-600 to-blue-600 text-white text-xs font-bold hover:from-violet-500 hover:to-blue-500"
              >
                Continue
              </button>
            </div>
          </form>
        )}

        <div className="pt-2 border-t border-slate-800 text-center">
          <button
            type="button"
            onClick={onClose}
            className="text-xs text-slate-500 hover:text-slate-300 transition-colors"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  )
}

export default function Login() {
  const navigate = useNavigate()
  const { user, loading, loginWithGoogle, loginWithEmail, signup, forgotPassword } = useAuth()

  const [mode, setMode] = useState(MODES.LOGIN)
  const [form, setForm] = useState({ name: '', email: '', password: '' })
  const [showPass, setShowPass] = useState(false)
  const [remember, setRemember] = useState(true)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [googleBusy, setGoogleBusy] = useState(false)
  const [stats, setStats] = useState({ totalFunding: 0, totalStartups: 0, activeInvestors: 0 })

  // If user is logged in after loading finishes, navigate to dashboard
  useEffect(() => {
    if (!loading && user) {
      navigate('/dashboard', { replace: true })
    }
  }, [user, loading, navigate])

  // Load stats for the hero panel
  useEffect(() => {
    fetchOverview()
      .then((d) => {
        if (d) setStats({ totalFunding: d.totalFundingB || 0, totalStartups: d.totalCompanies || 0, activeInvestors: d.activeInvestors || 0 })
      })
      .catch(() => {})
  }, [])

  const set = (k) => (e) => { setForm((f) => ({ ...f, [k]: e.target.value })); setError('') }
  const go = (m) => { setMode(m); setError('') }

  const [showGoogleModal, setShowGoogleModal] = useState(false)

  // ── Google sign-in ──────────────────────────────────────────────────────────
  const handleGoogle = async () => {
    setGoogleBusy(true)
    setError('')
    const res = await loginWithGoogle(remember)
    if (res.requiresAccountChoice) {
      setShowGoogleModal(true)
    } else if (res.success) {
      navigate('/dashboard')
    } else {
      setError(res.error || 'Google Sign-In failed. Please try again.')
    }
    setGoogleBusy(false)
  }

  const handleSelectGoogleAccount = async (account) => {
    setGoogleBusy(true)
    setShowGoogleModal(false)
    const res = await loginWithGoogle(remember, account)
    if (res.success) {
      navigate('/dashboard')
    } else {
      setError(res.error || 'Login failed. Please try again.')
    }
    setGoogleBusy(false)
  }

  // ── Email Login ─────────────────────────────────────────────────────────────
  const handleEmailLogin = async (e) => {
    e.preventDefault()
    if (!form.email.includes('@')) { setError('Please enter a valid email.'); return }
    if (form.password.length < 6) { setError('Password must be at least 6 characters.'); return }
    setBusy(true)
    setError('')
    const res = await loginWithEmail(form.email, form.password, remember)
    if (res.success) navigate('/dashboard')
    else setError(res.error)
    setBusy(false)
  }

  // ── Sign Up ─────────────────────────────────────────────────────────────────
  const handleSignup = async (e) => {
    e.preventDefault()
    if (!form.name.trim()) { setError('Full name is required.'); return }
    if (!form.email.includes('@')) { setError('Please enter a valid email.'); return }
    if (form.password.length < 6) { setError('Password must be at least 6 characters.'); return }
    setBusy(true)
    setError('')
    const res = await signup(form.name, form.email, form.password, remember)
    if (res.success) navigate('/dashboard')
    else setError(res.error)
    setBusy(false)
  }

  // ── Forgot Password ─────────────────────────────────────────────────────────
  const handleForgot = async (e) => {
    e.preventDefault()
    if (!form.email.includes('@')) { setError('Please enter your email address.'); return }
    setBusy(true)
    setError('')
    const res = await forgotPassword(form.email)
    if (res.success) go(MODES.FORGOT_SENT)
    else setError(res.error)
    setBusy(false)
  }

  // ══════════════════════════════════════════════════════════════════════════
  // FORM VIEWS
  // ══════════════════════════════════════════════════════════════════════════

  // Forgot Password Sent
  if (mode === MODES.FORGOT_SENT) {
    return (
      <PageShell stats={stats}>
        <div className="text-center">
          <CheckCircle className="h-14 w-14 text-emerald-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-white mb-2">Check your inbox</h2>
          <p className="text-slate-400 text-sm mb-6">
            Password reset link sent to {form.email}
          </p>
          <button
            type="button"
            onClick={() => go(MODES.LOGIN)}
            className="flex items-center justify-center gap-1.5 text-sm text-violet-400 bg-transparent border-none cursor-pointer hover:underline mx-auto"
          >
            <ArrowLeft size={14} /> Back to Sign In
          </button>
        </div>
      </PageShell>
    )
  }

  // Forgot Password Form
  if (mode === MODES.FORGOT) {
    return (
      <PageShell stats={stats}>
        <button
          type="button"
          onClick={() => go(MODES.LOGIN)}
          className="flex items-center gap-1.5 text-xs text-slate-400 bg-transparent border-none cursor-pointer hover:text-white mb-5"
        >
          <ArrowLeft size={13} /> Back
        </button>
        <h2 className="text-2xl font-bold text-white mb-1">Reset Password</h2>
        <p className="text-slate-400 text-sm mb-6">Enter your email and we'll send a reset link.</p>
        <ErrorBox error={error} />
        <form onSubmit={handleForgot} className="space-y-4 mt-3">
          <div>
            <label className={labelCls}>Email Address</label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={16} />
              <input className={inputCls + ' pl-9'} type="email" value={form.email} onChange={set('email')} placeholder="you@company.com" autoFocus />
            </div>
          </div>
          <button type="submit" disabled={busy} className={primaryBtn}>
            {busy ? 'Sending…' : 'Send Reset Link'}
          </button>
        </form>
      </PageShell>
    )
  }

  // ── Main Login / Signup ─────────────────────────────────────────────────────
  const isSignup = mode === MODES.SIGNUP

  return (
    <PageShell stats={stats}>
      {/* Title */}
      <h2 className="text-[26px] font-bold text-white text-center mb-1">
        {isSignup ? 'Create account' : 'Welcome back'}
      </h2>
      <p className="text-slate-400 text-sm text-center mb-6">
        {isSignup ? 'Sign up to access your analytics dashboard' : 'Sign in to your analytics dashboard'}
      </p>

      <ErrorBox error={error} />

      {/* ── Google Button ── */}
      <div className="mt-4">
        <GoogleButton onClick={handleGoogle} loading={googleBusy} />
      </div>

      {/* ── Divider ── */}
      <div className="relative my-5 text-center">
        <div className="absolute top-1/2 left-0 right-0 h-px bg-slate-800" />
        <span className="relative inline-block bg-slate-900 px-3 text-[11px] text-slate-500 uppercase tracking-wider">
          or continue with email
        </span>
      </div>

          {/* ── Email + Password ── */}
          <form onSubmit={isSignup ? handleSignup : handleEmailLogin} className="space-y-4" autoComplete="off">
            {isSignup && (
              <div>
                <label className={labelCls}>Full Name</label>
                <input className={inputCls} type="text" value={form.name} onChange={set('name')} placeholder="Your full name" autoComplete="off" />
              </div>
            )}

            <div>
              <label className={labelCls}>Email Address</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={15} />
                <input className={inputCls + ' pl-9'} type="email" value={form.email} onChange={set('email')} placeholder="you@company.com" autoComplete="off" />
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-1.5">
                <label className={labelCls + ' mb-0'}>Password</label>
                {!isSignup && (
                  <button
                    type="button"
                    onClick={() => go(MODES.FORGOT)}
                    className="text-[11px] text-violet-400 bg-transparent border-none cursor-pointer hover:underline"
                  >
                    Forgot password?
                  </button>
                )}
              </div>
              <div className="relative">
                <Shield className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={15} />
                <input
                  className={inputCls + ' pl-9 pr-10'}
                  type={showPass ? 'text' : 'password'}
                  value={form.password}
                  onChange={set('password')}
                  placeholder="••••••••"
                  autoComplete="new-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPass((p) => !p)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 bg-transparent border-none text-slate-500 cursor-pointer"
                >
                  {showPass ? <Eye size={15} /> : <EyeOff size={15} />}
                </button>
              </div>
            </div>

            {/* Remember Me */}
            <label className="flex items-center gap-2.5 cursor-pointer select-none">
              <div
                onClick={() => setRemember((r) => !r)}
                className={`w-4 h-4 rounded border-2 flex items-center justify-center transition-colors cursor-pointer ${remember ? 'bg-violet-600 border-violet-600' : 'border-slate-600 bg-transparent'}`}
              >
                {remember && <span className="text-white text-[9px] leading-none">✓</span>}
              </div>
              <span className="text-xs text-slate-400">Remember me for 30 days</span>
            </label>

            <button type="submit" disabled={busy} className={primaryBtn}>
              {busy ? 'Please wait…' : isSignup ? 'Create Account' : 'Sign In'}
            </button>
          </form>

          {/* ── Toggle signup / login ── */}
          <p className="text-center mt-5 text-xs text-slate-500">
            {isSignup ? 'Already have an account? ' : "Don't have an account? "}
            <button
              className="text-violet-400 bg-transparent border-none cursor-pointer font-semibold hover:underline text-xs"
              onClick={() => { setMode(isSignup ? MODES.LOGIN : MODES.SIGNUP); setError('') }}
            >
              {isSignup ? 'Sign in' : 'Sign up free'}
            </button>
          </p>

          {/* Google Account Selector Modal */}
          {showGoogleModal && (
            <GoogleAccountModal
              onClose={() => setShowGoogleModal(false)}
              onSelect={handleSelectGoogleAccount}
            />
          )}
    </PageShell>
  )
}

// ══════════════════════════════════════════════════════════════════════════════
// Page Shell — handles the two-column layout (hero + card)
// ══════════════════════════════════════════════════════════════════════════════
function PageShell({ stats, children }) {
  return (
    <div className="min-h-screen bg-slate-950 flex p-2.5">
      {/* Ambient glows */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -left-40 top-0 h-96 w-96 rounded-full bg-violet-700/15 blur-3xl" />
        <div className="absolute -right-40 bottom-0 h-96 w-96 rounded-full bg-blue-700/15 blur-3xl" />
      </div>

      <div className="relative mx-auto min-h-screen max-w-7xl grid-cols-2 items-center gap-12 px-6 lg:grid">
        {/* ── Left Hero Panel ── */}
        <div className="hidden lg:flex flex-col justify-center">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-violet-600 to-blue-500 shadow-lg shadow-violet-900/40">
              <TrendingUp className="h-5 w-5 text-white" />
            </div>
            <span className="text-sm font-bold tracking-wide text-violet-300">STARTUP FUNDING ANALYTICS</span>
          </div>

          <p className="mt-8 text-xs font-semibold tracking-[0.2em] text-violet-400">VENTURE INTELLIGENCE PLATFORM</p>
          <h1 className="mt-4 text-5xl font-extrabold leading-tight text-white">
            The smartest way to{' '}
            <span className="bg-gradient-to-r from-violet-400 to-blue-400 bg-clip-text text-transparent">
              track startup funding
            </span>
          </h1>
          <p className="mt-5 max-w-md text-slate-400">
            Real-time analytics, AI-powered predictions, and deep sector intelligence — all in one platform.
          </p>

          <ul className="mt-8 space-y-3.5">
            {FEATURES.map(({ icon: Icon, label }) => (
              <li key={label} className="flex items-center gap-3">
                <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-violet-500/10">
                  <Icon className="h-4 w-4 text-violet-400" />
                </span>
                <span className="text-sm text-slate-300">{label}</span>
              </li>
            ))}
          </ul>

          <div className="mt-10 grid grid-cols-3 gap-3 max-w-lg">
            {[
              { value: stats.totalFunding ? `$${stats.totalFunding}B` : '—', label: 'Total Funding' },
              { value: stats.totalStartups ? stats.totalStartups.toLocaleString() : '—', label: 'Startups' },
              { value: stats.activeInvestors || '—', label: 'Investors' },
            ].map(({ value, label }) => (
              <div key={label} className="rounded-xl border border-white/10 bg-slate-900 px-3 py-4">
                <p className="text-2xl font-extrabold text-white">{value}</p>
                <p className="mt-1 text-xs text-slate-400">{label}</p>
              </div>
            ))}
          </div>
        </div>

        {/* ── Right Auth Card ── */}
        <div className="flex justify-center mt-[8%] lg:mt-0">
          <div className="w-full max-w-md rounded-2xl border border-white/10 bg-slate-900 p-7 shadow-2xl">
            {children}
          </div>
        </div>
      </div>
    </div>
  )
}