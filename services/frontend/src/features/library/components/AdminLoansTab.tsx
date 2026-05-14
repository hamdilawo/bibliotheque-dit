import { useAtom, useAtomValue } from 'jotai'
import { loansAtom, booksAtom } from '../store'
import { AlertCircle, CheckCircle, Clock, Download, RotateCcw } from 'lucide-react'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'

function daysUntil(dateStr: string) {
  return Math.ceil((new Date(dateStr).getTime() - Date.now()) / 86400000)
}

function fmt(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })
}

const MOCK_USERS: Record<string, { name: string; email: string }> = {
  default: { name: 'Mamadou Diallo', email: 'mdiallo@dit.sn' },
}

function getUser(_loanId: string) {
  return MOCK_USERS.default
}

export function AdminLoansTab() {
  const [loans, setLoans] = useAtom(loansAtom)
  const books = useAtomValue(booksAtom)

  const overdue = loans.filter((l) => l.status === 'overdue')
  const active = loans.filter((l) => l.status === 'active')
  const returned = loans.filter((l) => l.status === 'returned')

  const handleExportCSV = () => {
    const header = ['loan_id', 'book_id', 'book_title', 'book_author', 'date_emprunt', 'date_retour_prevue', 'date_retour_effective', 'statut', 'rating']
    const rows = loans.map((l) => {
      const book = books.find((b) => b.id === l.bookId)
      return [
        l.id,
        l.bookId,
        book?.title ?? '',
        book?.author ?? '',
        l.borrowedAt,
        l.dueAt,
        l.returnedAt ?? '',
        l.status,
        '',
      ]
    })
    const csv = [header, ...rows].map((r) => r.map((v) => `"${v}"`).join(',')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'loans.csv'
    a.click()
    URL.revokeObjectURL(url)
    toast.success('loans.csv exporté', { description: `${loans.length} emprunts` })
  }

  const handleReturn = (loanId: string, _bookId: string) => {
    setLoans(loans.map((l) =>
      l.id === loanId ? { ...l, status: 'returned', returnedAt: new Date().toISOString() } : l
    ))
    toast.success('Retour validé')
  }

  const LoanRow = ({ loan }: { loan: typeof loans[0] }) => {
    const book = books.find((b) => b.id === loan.bookId)
    const user = getUser(loan.id)
    const daysLeft = daysUntil(loan.dueAt)
    const isOverdue = loan.status === 'overdue'
    const isReturned = loan.status === 'returned'

    return (
      <div className={cn(
        'flex items-center gap-3 bg-white rounded-2xl border p-3 shadow-sm',
        isOverdue ? 'border-red-100' : isReturned ? 'border-gray-100 opacity-60' : 'border-gray-100'
      )}>
        <div
          className="w-9 h-9 rounded-xl flex items-center justify-center text-white text-sm font-bold flex-shrink-0"
          style={{ backgroundColor: isOverdue ? '#ef4444' : isReturned ? '#9ca3af' : '#004455' }}
        >
          {user.name.charAt(0)}
        </div>
        <div className="flex-1 min-w-0">
          <p className="font-semibold text-gray-900 text-xs line-clamp-1">{user.name}</p>
          <p className="text-gray-400 text-xs line-clamp-1">{book?.title ?? '—'}</p>
          <div className="flex items-center gap-1 mt-0.5">
            {isOverdue ? (
              <span className="text-xs font-semibold text-red-500 flex items-center gap-0.5">
                <AlertCircle className="w-3 h-3" /> {Math.abs(daysLeft)}j de retard
              </span>
            ) : isReturned ? (
              <span className="text-xs text-emerald-500 flex items-center gap-0.5">
                <CheckCircle className="w-3 h-3" /> Rendu {fmt(loan.returnedAt!)}
              </span>
            ) : (
              <span className="text-xs text-amber-500 flex items-center gap-0.5">
                <Clock className="w-3 h-3" /> Retour {fmt(loan.dueAt)}
              </span>
            )}
          </div>
        </div>
        {!isReturned && (
          <button
            onClick={() => handleReturn(loan.id, loan.bookId)}
            className={cn(
              'flex items-center gap-1 text-xs font-semibold px-2.5 py-1.5 rounded-lg border transition-colors',
              isOverdue
                ? 'border-red-200 text-red-500 hover:bg-red-50'
                : 'border-gray-200 text-gray-500 hover:bg-gray-50'
            )}
          >
            <RotateCcw className="w-3 h-3" />
            Retour
          </button>
        )}
      </div>
    )
  }

  const Section = ({
    title,
    loans: list,
    dot,
  }: {
    title: string
    loans: typeof loans
    dot: string
  }) => {
    if (list.length === 0) return null
    return (
      <div className="mb-5">
        <div className="flex items-center gap-2 mb-2">
          <span className={`w-2 h-2 rounded-full ${dot}`} />
          <h2 className="font-bold text-gray-800 text-sm">{title} ({list.length})</h2>
        </div>
        <div className="space-y-2">
          {list.map((l) => <LoanRow key={l.id} loan={l} />)}
        </div>
      </div>
    )
  }

  return (
    <div className="px-5">
      <div className="flex justify-end mb-4">
        <button
          onClick={handleExportCSV}
          className="flex items-center gap-1.5 text-xs font-semibold px-3 py-2 rounded-xl border border-gray-200 bg-white text-gray-600 hover:bg-gray-50 shadow-sm transition-colors"
        >
          <Download className="w-3.5 h-3.5" />
          Exporter CSV
        </button>
      </div>
      <Section title="En retard" loans={overdue} dot="bg-red-500" />
      <Section title="En cours" loans={active} dot="bg-amber-400" />
      <Section title="Rendus" loans={returned} dot="bg-emerald-400" />
      {loans.length === 0 && (
        <p className="text-center text-gray-400 text-sm py-10">Aucun emprunt enregistré.</p>
      )}
    </div>
  )
}
