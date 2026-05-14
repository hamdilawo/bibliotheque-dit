import { useAtom, useAtomValue, useSetAtom } from 'jotai'
import { loansAtom, booksAtom, isAuthenticatedAtom, loginSheetOpenAtom } from '../store'
import { AlertCircle, BookMarked, CheckCircle, Clock, LogIn, Lock } from 'lucide-react'
import { cn } from '@/lib/utils'
import { toast } from 'sonner'

function daysUntil(dateStr: string) {
  return Math.ceil((new Date(dateStr).getTime() - Date.now()) / 86400000)
}

function fmt(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })
}

export function LoansView() {
  const isAuthenticated = useAtomValue(isAuthenticatedAtom)
  const setLoginOpen = useSetAtom(loginSheetOpenAtom)
  const [loans, setLoans] = useAtom(loansAtom)
  const [books, setBooks] = useAtom(booksAtom)

  const active = loans.filter((l) => l.status === 'active' || l.status === 'overdue')
  const returned = loans.filter((l) => l.status === 'returned')

  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-[70vh] px-5">
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

  const handleReturn = (loanId: string, bookId: string, title: string) => {
    setLoans(loans.map((l) =>
      l.id === loanId ? { ...l, status: 'returned', returnedAt: new Date().toISOString() } : l
    ))
    setBooks(books.map((b) => (b.id === bookId ? { ...b, available: b.available + 1 } : b)))
    toast.success('Livre rendu !', { description: `"${title}" a été retourné` })
  }

  return (
    <div className="pb-6">
      <div className="px-5 pt-2 mb-6">
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Suivi</p>
        <h1 className="text-2xl font-bold text-gray-900 mt-1">Mes emprunts</h1>
      </div>

      <div className="px-5 mb-6">
        <div className="flex items-center gap-2 mb-3">
          <BookMarked className="w-4 h-4" style={{ color: '#004455' }} />
          <h2 className="font-bold text-gray-800 text-sm">En cours ({active.length})</h2>
        </div>

        {active.length === 0 ? (
          <div className="text-center py-10 bg-white rounded-2xl border border-gray-100">
            <BookMarked className="w-10 h-10 text-gray-200 mx-auto mb-2" />
            <p className="text-gray-400 text-sm font-medium">Aucun emprunt en cours</p>
          </div>
        ) : (
          <div className="space-y-3">
            {active.map((loan) => {
              const book = books.find((b) => b.id === loan.bookId)
              if (!book) return null
              const daysLeft = daysUntil(loan.dueAt)
              const isOverdue = loan.status === 'overdue'

              return (
                <div key={loan.id} className="bg-white rounded-2xl border border-gray-100 overflow-hidden flex shadow-sm">
                  <img src={book.coverUrl} alt={book.title} className="w-20 h-28 object-cover flex-shrink-0" />
                  <div className="flex-1 p-3 flex flex-col justify-between min-w-0">
                    <div>
                      <p className="font-semibold text-gray-900 text-sm leading-tight line-clamp-2">{book.title}</p>
                      <p className="text-gray-400 text-xs mt-0.5 line-clamp-1">{book.author}</p>
                    </div>
                    <div className="space-y-1">
                      <div
                        className={cn(
                          'flex items-center gap-1 text-xs font-semibold',
                          isOverdue ? 'text-rose-500' : daysLeft <= 3 ? 'text-amber-500' : 'text-emerald-500'
                        )}
                      >
                        {isOverdue ? (
                          <>
                            <AlertCircle className="w-3 h-3" />
                            En retard de {Math.abs(daysLeft)}j
                          </>
                        ) : (
                          <>
                            <Clock className="w-3 h-3" />
                            {daysLeft}j restants
                          </>
                        )}
                      </div>
                      <p className="text-gray-300 text-xs">Retour : {fmt(loan.dueAt)}</p>
                      <button
                        onClick={() => handleReturn(loan.id, book.id, book.title)}
                        className="text-xs font-semibold py-1.5 px-3 rounded-lg border border-gray-200 text-gray-600 active:scale-95 transition-transform"
                      >
                        Rendre
                      </button>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {returned.length > 0 && (
        <div className="px-5">
          <div className="flex items-center gap-2 mb-3">
            <CheckCircle className="w-4 h-4 text-gray-400" />
            <h2 className="font-bold text-gray-800 text-sm">Historique ({returned.length})</h2>
          </div>
          <div className="space-y-2">
            {returned.map((loan) => {
              const book = books.find((b) => b.id === loan.bookId)
              if (!book) return null
              return (
                <div key={loan.id} className="flex items-center gap-3 bg-white rounded-xl p-3 border border-gray-100 opacity-70">
                  <img src={book.coverUrl} alt={book.title} className="w-12 h-16 object-cover rounded-lg flex-shrink-0" />
                  <div className="min-w-0">
                    <p className="font-medium text-gray-800 text-sm line-clamp-1">{book.title}</p>
                    <p className="text-gray-400 text-xs line-clamp-1">{book.author}</p>
                    <div className="flex items-center gap-1 mt-1 text-emerald-500">
                      <CheckCircle className="w-3 h-3" />
                      <span className="text-xs">Rendu le {fmt(loan.returnedAt!)}</span>
                    </div>
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
