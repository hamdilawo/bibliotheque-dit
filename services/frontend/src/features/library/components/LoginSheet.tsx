import { useState } from 'react'
import { useAtom, useSetAtom } from 'jotai'
import { loginSheetOpenAtom, isAuthenticatedAtom, currentUserAtom, accessTokenAtom } from '../store'
import { AnimatePresence, motion } from 'framer-motion'
import { X, LogIn, Mail, Lock, AlertCircle } from 'lucide-react'

export function LoginSheet() {
  const [open, setOpen] = useAtom(loginSheetOpenAtom)
  const setAuthenticated = useSetAtom(isAuthenticatedAtom)
  const setCurrentUser = useSetAtom(currentUserAtom)
  const setToken = useSetAtom(accessTokenAtom)

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const res = await fetch('http://localhost:8002/api/auth/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })
      const data = await res.json()
      if (!res.ok) {
        throw new Error(data.detail ?? 'Email ou mot de passe incorrect.')
      }
      setCurrentUser({ id: data.id, email: data.email, full_name: data.full_name, role: data.role })
      setToken(data.access)
      setAuthenticated(true)
      setOpen(false)
      setEmail('')
      setPassword('')
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleClose = () => {
    setOpen(false)
    setError(null)
  }

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            className="fixed inset-0 bg-black/60 z-40 backdrop-blur-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={handleClose}
          />
          <motion.div
            className="fixed bottom-0 left-0 right-0 z-50 flex justify-center"
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
          >
            <div className="w-full max-w-2xl">
              <div className="relative overflow-hidden rounded-t-3xl border border-border/70 bg-card/95 px-6 pb-10 pt-6 shadow-2xl backdrop-blur">
                {/* blobs */}
                <div className="pointer-events-none absolute -left-16 -top-20 h-56 w-56 rounded-full bg-primary/10 blur-3xl" />
                <div className="pointer-events-none absolute -bottom-24 -right-10 h-64 w-64 rounded-full bg-secondary/25 blur-3xl" />

                <div className="relative z-10">
                  {/* Header */}
                  <div className="flex items-center justify-between mb-6">
                    <div>
                      <p className="text-xs uppercase tracking-[0.3em] text-muted-foreground">DIT Library</p>
                      <h2 className="text-xl font-semibold tracking-tight text-foreground mt-0.5">Connexion</h2>
                    </div>
                    <button
                      onClick={handleClose}
                      className="w-8 h-8 rounded-full bg-muted flex items-center justify-center hover:bg-accent transition-colors"
                    >
                      <X className="w-4 h-4 text-muted-foreground" />
                    </button>
                  </div>

                  <form onSubmit={handleSubmit} className="space-y-4">
                    {error && (
                      <div className="flex items-center gap-2 text-sm text-destructive bg-destructive/10 rounded-xl px-3 py-2.5">
                        <AlertCircle className="w-4 h-4 flex-shrink-0" />
                        {error}
                      </div>
                    )}

                    <div className="space-y-1.5">
                      <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                        Adresse email
                      </label>
                      <div className="relative">
                        <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                        <input
                          type="email"
                          value={email}
                          onChange={(e) => setEmail(e.target.value)}
                          placeholder="prenom.nom@dit.sn"
                          required
                          className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-border bg-background text-sm text-foreground placeholder:text-muted-foreground/60 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/50 transition-all"
                        />
                      </div>
                    </div>

                    <div className="space-y-1.5">
                      <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                        Mot de passe
                      </label>
                      <div className="relative">
                        <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                        <input
                          type="password"
                          value={password}
                          onChange={(e) => setPassword(e.target.value)}
                          placeholder="••••••••"
                          required
                          className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-border bg-background text-sm text-foreground placeholder:text-muted-foreground/60 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/50 transition-all"
                        />
                      </div>
                    </div>

                    <button
                      type="submit"
                      disabled={loading}
                      className="w-full flex items-center justify-center gap-2 rounded-full border border-primary bg-primary py-2.5 text-sm font-medium text-primary-foreground shadow-sm hover:opacity-90 transition-opacity disabled:opacity-50"
                    >
                      {loading ? (
                        <span className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
                      ) : (
                        <LogIn className="w-4 h-4" />
                      )}
                      {loading ? 'Connexion...' : 'Se connecter'}
                    </button>
                  </form>
                </div>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
