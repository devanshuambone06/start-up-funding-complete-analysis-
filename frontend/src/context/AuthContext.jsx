/**
 * AuthContext.jsx — Global authentication state management
 * Supports: Google OAuth, Email+Password, RememberMe, Logout
 */
import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import {
  signInWithGoogle as fbGoogle,
  loginWithEmail as fbLoginEmail,
  registerWithEmail as fbRegisterEmail,
  resetPassword as fbResetPassword,
  firebaseSignOut,
  onFirebaseAuthChange,
} from '../services/auth'

const AuthContext = createContext(null)

const SESSION_KEY = 'sfa_user'
const REMEMBER_KEY = 'sfa_remember'

function saveUser(userData, remember) {
  const store = remember ? localStorage : sessionStorage
  store.setItem(SESSION_KEY, JSON.stringify(userData))
  if (remember) localStorage.setItem(REMEMBER_KEY, '1')
}

function loadUser() {
  try {
    const remember = localStorage.getItem(REMEMBER_KEY)
    if (remember) {
      const stored = localStorage.getItem(SESSION_KEY)
      if (stored) return JSON.parse(stored)
    }
  } catch (_) { /* ignore */ }
  return null
}

function clearUser() {
  localStorage.removeItem(SESSION_KEY)
  localStorage.removeItem(REMEMBER_KEY)
  sessionStorage.removeItem(SESSION_KEY)
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  // Listen to authentication state on mount
  useEffect(() => {
    // onFirebaseAuthChange will call callback once Firebase resolves.
    // If Firebase is not configured (no auth), it returns null immediately.
    // We only fall back to localStorage AFTER Firebase says "no user".
    const unsub = onFirebaseAuthChange((firebaseUser) => {
      if (firebaseUser) {
        // Real Firebase user logged in
        const userData = {
          uid: firebaseUser.uid,
          email: firebaseUser.email,
          name: firebaseUser.displayName || firebaseUser.email?.split('@')[0] || 'User',
          photoURL: firebaseUser.photoURL,
          provider: firebaseUser.providerData?.[0]?.providerId || 'google',
        }
        const remember = !!localStorage.getItem(REMEMBER_KEY)
        saveUser(userData, remember)
        setUser(userData)
        setLoading(false)
      } else {
        // Firebase says no user — now check if we have a stored fallback session
        // (e.g., a Google fallback user saved after API key error)
        const stored = loadUser()
        if (stored) {
          setUser(stored)
        } else {
          clearUser()
          setUser(null)
        }
        setLoading(false)
      }
    })

    return () => {
      unsub()
    }
  }, [])

  // ── Google Sign-In ──────────────────────────────────────────────────────────
  const loginWithGoogle = useCallback(async (remember = true) => {
    const res = await fbGoogle()
    if (res.success && res.user) {
      saveUser(res.user, remember)
      setUser(res.user)
    }
    return res
  }, [])

  // ── Email Login ─────────────────────────────────────────────────────────────
  const loginWithEmail = useCallback(async (email, password, remember = false) => {
    const res = await fbLoginEmail(email, password)
    if (res.success && res.user) {
      saveUser(res.user, remember)
      setUser(res.user)
    }
    return res
  }, [])

  // ── Email Sign Up ───────────────────────────────────────────────────────────
  const signup = useCallback(async (name, email, password, remember = false) => {
    const res = await fbRegisterEmail(name, email, password)
    if (res.success && res.user) {
      saveUser(res.user, remember)
      setUser(res.user)
    }
    return res
  }, [])

  // ── Password Reset ──────────────────────────────────────────────────────────
  const forgotPassword = useCallback(async (email) => {
    return fbResetPassword(email)
  }, [])

  // ── Logout ──────────────────────────────────────────────────────────────────
  const logout = useCallback(async () => {
    await firebaseSignOut()
    clearUser()
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{
      user,
      loading,
      loginWithGoogle,
      loginWithEmail,
      signup,
      forgotPassword,
      logout,
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within <AuthProvider>')
  return ctx
}
