import { useEffect, useState } from 'react'
import { useAtom, useAtomValue, useSetAtom } from 'jotai'
import { loansAtom, booksAtom, isAuthenticatedAtom, loginSheetOpenAtom, currentUserAtom, accessTokenAtom } from '../store'
import { AlertCircle, BookMarked, CheckCircle, Clock, Loader2, LogIn, Lock, RotateCcw } from 'lucide-react'
import { cn } from '@/lib/utils'
import { toast } from 'sonner'
import { fetchMyLoans, returnBook } from '../api'

function daysUntil(dateStr: string) {
  return Math.ceil((new Date(dateStr).getTime() - Date.now()) / 86400000)
}

function fmt(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })
}

function progressPercent(borrowedAt: string, dueAt: string) {
  const total = new Date(dueAt).getTime() - new Date(borrowedAt).getTime()
  const elapsed = Date.now() - new Date(borrowedAt).getTime()
  return Math.min(100, Math.max(0, (elapsed / total) * 100))
}

export function LoansView() {
  const isAuthenticated = useAtomValue(isAuthenticatedAtom)
  const currentUser = useAtomValue(currentUserAtom)
  const token = useAtomValue(accessTokenAtom)
  const setLoginOpen = useSetAtom(loginSheetOpenAtom)
  const [loans, setLoans] = useAtom(loansAtom)
  const books = useAtomValue(booksAtom)
  const [loading, setLoading] = useState(false)
  const [returning, setReturning] = useState<string | null>(null)

  useEffect(() => {
    if (!isAuthenticated || !token || !currentUser) return
    setLoading(true)
    fetchMyLoans(token, currentUser.id)
      .then(setLoans)
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [isAuthenticated])

  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-[70vh] px-4">
        <div className="relative w-full overflow-hidden rounded-3xl border border-border/70 bg-card/80 p-10 text-center shadow-2xl backdrop-blur">
          <div className="pointer-events-none absolute -left-16 -top-20 h-56 w-56 rounded-full bg-primary/10 blur-3xl" />
          <div className="pointer-events-none absolute -bottom-24 -right-10 h-64 w-64 rounded-full bg-secondary/25 blur-3xl" />
          <div className="relative z-10 space-y-4">
            <p className="text-xs uppercase tracking-[0.3em] text-muted-foreground">Accès requis</p>
            <div className="flex justify-center">
              <Lock className="w-10 h-10 text-primary/60" />
            </div>
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">Mes emprunts</h2>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Connectez-vous pour consulter vos emprunts en cours et suivre vos retours.
            </p>
            <div className="mt-6 flex justify-center">
              <button
                onClick={() => setLoginOpen(true)}
                className="flex items-center gap-2 rounded-full border border-primary bg-primary px-5 py-2 text-sm font-medium text-primary-foreground shadow-sm hover:opacity-90 transition-opacity"
              >
                <LogIn className="w-4 h-4" />
                Se connecter
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
      </div>
    )
  }

  const handleReturn = async (loanId: string, title: string) => {
    if (!token || !currentUser) return
    setReturning(loanId)
    try {
      await returnBook(loanId, token)
      const fresh = await fetchMyLoans(token, currentUser.id)
      setLoans(fresh)
      toast.success('Livre rendu !', { description: `"${title}" a été retourné` })
    } catch (e: any) {
      toast.error(e.message)
    } finally {
      setReturning(null)
    }
  }

  const active = loans.filter((l) => l.status === 'active' || l.status === 'overdue')
  const returned = loans.filter((l) => l.status === 'returned')

  return (
    <div className="pb-8 px-4">

      {/* ── Header ── */}
      <div className="pt-2 mb-5 flex items-end justify-between">
        <div>
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Suivi</p>
          <h1 className="text-2xl font-bold text-gray-900 mt-0.5">Mes emprunts</h1>
        </div>
        {active.length > 0 && (
          <div
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold"
            style={{ backgroundColor: '#00445515', color: '#004455' }}
          >
            <BookMarked className="w-3.5 h-3.5" />
            {active.length} en cours
          </div>
        )}
      </div>

      {/* ── Active loans ── */}
      {active.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16 bg-white rounded-3xl border border-gray-100 mb-4">
          <div className="w-14 h-14 rounded-2xl flex items-center justify-center mb-3" style={{ backgroundColor: '#00445510' }}>
            <BookMarked className="w-7 h-7" style={{ color: '#004455' }} />
          </div>
          <p className="font-semibold text-gray-700 text-sm">Aucun emprunt en cours</p>
          <p className="text-gray-400 text-xs mt-1">Parcourez la bibliothèque pour emprunter</p>
        </div>
      ) : (
        <div className="space-y-3 mb-6">
          {active.map((loan) => {
            const book = books.find((b) => b.id === loan.bookId)
            const daysLeft = daysUntil(loan.dueAt)
            const isOverdue = loan.status === 'overdue' || daysLeft < 0
            const isUrgent = !isOverdue && daysLeft <= 3
            const progress = progressPercent(loan.borrowedAt, loan.dueAt)
            const title = book?.title ?? 'Livre'
            const author = book?.author ?? ''
            const cover = book?.coverUrl ?? `https://picsum.photos/seed/${loan.bookId}/300/450`

            const statusColor = isOverdue ? '#ef4444' : isUrgent ? '#f59e0b' : '#10b981'
            const statusBg = isOverdue ? '#fef2f2' : isUrgent ? '#fffbeb' : '#f0fdf4'

            return (
              <div
                key={loan.id}
                className="bg-white rounded-2xl overflow-hidden shadow-sm border border-gray-100"
              >
                <div className="flex gap-4 p-4">
                  {/* Cover */}
                  <div className="relative flex-shrink-0">
                    <img
                      src={cover}
                      alt={title}
                      className="w-16 h-24 object-cover rounded-xl shadow-md"
                    />
                    {isOverdue && (
                      <div className="absolute -top-1.5 -right-1.5 w-5 h-5 rounded-full bg-red-500 flex items-center justify-center">
                        <AlertCircle className="w-3 h-3 text-white" />
                      </div>
                    )}
                  </div>

                  {/* Info */}
                  <div className="flex-1 min-w-0 flex flex-col justify-between">
                    <div>
                      <p className="font-bold text-gray-900 text-sm leading-snug line-clamp-2">{title}</p>
                      <p className="text-gray-400 text-xs mt-0.5">{author}</p>
                    </div>

                    {/* Dates row */}
                    <div className="flex items-center justify-between mt-2">
                      <div
                        className="flex items-center gap-1 text-xs font-semibold px-2 py-1 rounded-lg"
                        style={{ backgroundColor: statusBg, color: statusColor }}
                      >
                        {isOverdue
                          ? <><AlertCircle className="w-3 h-3" />{Math.abs(daysLeft)}j de retard</>
                          : <><Clock className="w-3 h-3" />{daysLeft}j restants</>
                        }
                      </div>
                      <span className="text-xs text-gray-400">
                        Retour {fmt(loan.dueAt)}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Progress bar */}
                <div className="px-4 pb-1">
                  <div className="h-1 w-full bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all"
                      style={{
                        width: `${progress}%`,
                        backgroundColor: statusColor,
                      }}
                    />
                  </div>
                </div>

                {/* Return button */}
                <div className="px-4 pb-4 pt-2.5">
                  <button
                    onClick={() => handleReturn(loan.id, title)}
                    disabled={returning === loan.id}
                    className={cn(
                      'w-full flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-semibold transition-all active:scale-[0.98] disabled:opacity-50',
                      isOverdue
                        ? 'bg-red-50 text-red-600 border border-red-200 hover:bg-red-100'
                        : 'bg-gray-50 text-gray-700 border border-gray-200 hover:bg-gray-100'
                    )}
                  >
                    {returning === loan.id
                      ? <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      : <RotateCcw className="w-3.5 h-3.5" />
                    }
                    Rendre le livre
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* ── History ── */}
      {returned.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <CheckCircle className="w-4 h-4 text-gray-300" />
            <h2 className="font-bold text-gray-500 text-xs uppercase tracking-wider">Historique · {returned.length}</h2>
          </div>
          <div className="space-y-2">
            {returned.map((loan) => {
              const book = books.find((b) => b.id === loan.bookId)
              const title = book?.title ?? 'Livre'
              const author = book?.author ?? ''
              const cover = book?.coverUrl ?? `https://picsum.photos/seed/${loan.bookId}/300/450`
              return (
                <div key={loan.id} className="flex items-center gap-3 bg-white/60 rounded-2xl p-3 border border-gray-100">
                  <img
                    src={cover}
                    alt={title}
                    className="w-10 h-14 object-cover rounded-lg flex-shrink-0 opacity-60"
                  />
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-gray-600 text-sm line-clamp-1">{title}</p>
                    <p className="text-gray-400 text-xs line-clamp-1">{author}</p>
                  </div>
                  <div className="flex items-center gap-1 text-emerald-500 flex-shrink-0">
                    <CheckCircle className="w-3.5 h-3.5" />
                    <span className="text-xs font-medium">{fmt(loan.returnedAt!)}</span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
