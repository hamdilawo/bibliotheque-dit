import { useAtomValue, useSetAtom } from 'jotai'
import { loansAtom, isAuthenticatedAtom, loginSheetOpenAtom, currentUserAtom } from '../store'
import { Award, BookOpen, GraduationCap, Lock, LogIn, LogOut, Mail } from 'lucide-react'

export function AccountView() {
  const isAuthenticated = useAtomValue(isAuthenticatedAtom)
  const setLoginOpen = useSetAtom(loginSheetOpenAtom)
  const currentUser = useAtomValue(currentUserAtom)
  const setAuthenticated = useSetAtom(isAuthenticatedAtom)
  const setCurrentUser = useSetAtom(currentUserAtom)

  const handleLogout = () => {
    setAuthenticated(false)
    setCurrentUser(null)
  }
  const loans = useAtomValue(loansAtom)

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
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">Mon profil</h2>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Connectez-vous pour accéder à votre profil, vos statistiques et vos badges.
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
  const total = loans.length
  const returned = loans.filter((l) => l.status === 'returned').length
  const active = loans.filter((l) => l.status === 'active' || l.status === 'overdue').length

  return (
    <div className="pb-6 px-5">
      <div className="pt-2 mb-6">
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Mon profil</p>
        <h1 className="text-2xl font-bold text-gray-900 mt-1">Compte</h1>
      </div>

      <div className="flex items-center gap-4 bg-white rounded-2xl p-4 border border-gray-100 mb-3 shadow-sm">
        <div
          className="w-16 h-16 rounded-2xl flex items-center justify-center text-white text-2xl font-bold flex-shrink-0"
          style={{ backgroundColor: '#004455' }}
        >
          {(currentUser?.full_name ?? '?').charAt(0)}
        </div>
        <div>
          <p className="font-bold text-gray-900">{currentUser?.full_name}</p>
          <p className="text-sm text-gray-500 mt-0.5">{currentUser?.email}</p>
          <span
            className="text-xs font-semibold px-2.5 py-0.5 rounded-full mt-1.5 inline-block"
            style={{ backgroundColor: '#00445515', color: '#004455' }}
          >
            {currentUser?.role}
          </span>
        </div>
      </div>

      <div className="flex items-center gap-3 bg-white rounded-2xl p-4 border border-gray-100 mb-5">
        <Mail className="w-4 h-4 text-gray-400 flex-shrink-0" />
        <span className="text-sm text-gray-600">{currentUser?.email}</span>
      </div>

      <h2 className="font-bold text-gray-900 text-sm mb-3">Statistiques</h2>
      <div className="grid grid-cols-3 gap-3 mb-6">
        <div className="bg-white rounded-2xl p-3 border border-gray-100 text-center shadow-sm">
          <p className="text-2xl font-bold" style={{ color: '#004455' }}>{total}</p>
          <p className="text-xs text-gray-400 mt-0.5">Total</p>
        </div>
        <div className="bg-white rounded-2xl p-3 border border-gray-100 text-center shadow-sm">
          <p className="text-2xl font-bold text-emerald-500">{returned}</p>
          <p className="text-xs text-gray-400 mt-0.5">Rendus</p>
        </div>
        <div className="bg-white rounded-2xl p-3 border border-gray-100 text-center shadow-sm">
          <p className="text-2xl font-bold text-amber-500">{active}</p>
          <p className="text-xs text-gray-400 mt-0.5">En cours</p>
        </div>
      </div>

      <h2 className="font-bold text-gray-900 text-sm mb-3">Badges</h2>
      <div className="space-y-2">
        {total >= 1 && (
          <div className="flex items-center gap-3 bg-white rounded-xl p-3 border border-gray-100">
            <div className="w-10 h-10 rounded-xl bg-amber-50 flex items-center justify-center flex-shrink-0">
              <Award className="w-5 h-5 text-amber-500" />
            </div>
            <div>
              <p className="font-semibold text-sm text-gray-800">Premier emprunt</p>
              <p className="text-xs text-gray-400">Vous avez emprunté votre premier livre</p>
            </div>
          </div>
        )}
        {total >= 3 && (
          <div className="flex items-center gap-3 bg-white rounded-xl p-3 border border-gray-100">
            <div className="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center flex-shrink-0">
              <BookOpen className="w-5 h-5 text-blue-500" />
            </div>
            <div>
              <p className="font-semibold text-sm text-gray-800">Lecteur assidu</p>
              <p className="text-xs text-gray-400">3 livres empruntés ou plus</p>
            </div>
          </div>
        )}
        {returned >= 1 && (
          <div className="flex items-center gap-3 bg-white rounded-xl p-3 border border-gray-100">
            <div
              className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
              style={{ backgroundColor: '#00445512' }}
            >
              <GraduationCap className="w-5 h-5" style={{ color: '#004455' }} />
            </div>
            <div>
              <p className="font-semibold text-sm text-gray-800">Citoyen exemplaire</p>
              <p className="text-xs text-gray-400">Livres rendus dans les délais</p>
            </div>
          </div>
        )}
      </div>

      <button
        onClick={handleLogout}
        className="mt-6 w-full flex items-center justify-center gap-2 py-2.5 rounded-xl border border-red-200 text-red-500 text-sm font-medium hover:bg-red-50 transition-colors"
      >
        <LogOut className="w-4 h-4" />
        Se déconnecter
      </button>
    </div>
  )
}
