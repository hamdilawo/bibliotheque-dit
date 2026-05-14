import { useState, useEffect } from 'react'
import { useAtomValue, useSetAtom } from 'jotai'
import { activeViewAtom, loginSheetOpenAtom, isAuthenticatedAtom, currentUserAtom, accessTokenAtom, loansAtom } from '../store'
import { fetchMyLoans } from '../api'
import { FloatingNav } from './FloatingNav'
import { DiscoverView } from './DiscoverView'
import { LoansView } from './LoansView'
import { AccountView } from './AccountView'
import { AdminView } from './AdminView'
import { BookDetailSheet } from './BookDetailSheet'
import { LoginSheet } from './LoginSheet'
import { AnimatePresence, motion } from 'framer-motion'
import { LogOut, ShieldCheck, X, Check } from 'lucide-react'

const VIEWS = {
  discover: DiscoverView,
  loans: LoansView,
  account: AccountView,
  admin: AdminView,
}

export function LibraryShell() {
  const active = useAtomValue(activeViewAtom)
  const setLoginOpen = useSetAtom(loginSheetOpenAtom)
  const isAuthenticated = useAtomValue(isAuthenticatedAtom)
  const currentUser = useAtomValue(currentUserAtom)
  const setAuthenticated = useSetAtom(isAuthenticatedAtom)
  const setCurrentUser = useSetAtom(currentUserAtom)
  const token = useAtomValue(accessTokenAtom)
  const setToken = useSetAtom(accessTokenAtom)
  const setLoans = useSetAtom(loansAtom)
  const [confirmLogout, setConfirmLogout] = useState(false)
  const ActiveView = VIEWS[active as keyof typeof VIEWS]

  useEffect(() => {
    if (!isAuthenticated || !token || !currentUser) return
    fetchMyLoans(token, currentUser.id).then(setLoans).catch(() => {})
  }, [isAuthenticated])

  const handleLogout = () => {
    setAuthenticated(false)
    setCurrentUser(null)
    setToken(null)
    setConfirmLogout(false)
  }

  return (
    <div className="lib-bg min-h-screen">
      <div className="max-w-2xl mx-auto relative">
        {/* Minimal top bar */}
        <div className="sticky top-0 z-20 px-2 py-3">
          <div className="flex items-center justify-between bg-white/60 backdrop-blur-md rounded-2xl px-4 py-2.5 shadow-sm shadow-black/5 border border-white/70">
            <div className="flex items-center gap-2.5">
              <div
                className="w-8 h-8 rounded-xl flex items-center justify-center shadow-sm"
                style={{ backgroundColor: '#004455' }}
              >
                <span className="text-white text-sm font-black">D</span>
              </div>
              <span className="font-bold text-gray-900 text-sm tracking-tight">DIT Library</span>
            </div>
            {isAuthenticated ? (
              confirmLogout ? (
                <div className="flex items-center gap-1.5">
                  <button
                    onClick={() => setConfirmLogout(false)}
                    className="flex items-center justify-center w-7 h-7 rounded-full border border-gray-200 bg-white/70 hover:bg-gray-100 transition-colors"
                  >
                    <X className="w-3.5 h-3.5 text-gray-500" />
                  </button>
                  <button
                    onClick={handleLogout}
                    className="flex items-center gap-1 px-3 py-1.5 rounded-full bg-red-500 hover:bg-red-600 transition-colors text-white text-xs font-semibold"
                  >
                    <Check className="w-3 h-3" />
                    Confirmer
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => setConfirmLogout(true)}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-gray-200 bg-white/70 backdrop-blur-sm hover:bg-red-50 hover:border-red-200 transition-colors cursor-pointer group"
                >
                  <span className="text-xs font-semibold text-gray-600 group-hover:text-red-500 transition-colors">
                    {currentUser?.full_name?.split(' ')[0]}
                  </span>
                  <LogOut className="w-3.5 h-3.5 text-gray-400 group-hover:text-red-500 transition-colors" />
                </button>
              )
            ) : (
              <button
                onClick={() => setLoginOpen(true)}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-[#004455]/20 bg-white/70 backdrop-blur-sm hover:bg-[#004455]/5 transition-colors cursor-pointer"
              >
                <ShieldCheck className="w-3.5 h-3.5" style={{ color: '#004455' }} />
                <span className="text-xs font-semibold" style={{ color: '#004455' }}>Personnel DIT</span>
              </button>
            )}
          </div>
        </div>

        <AnimatePresence mode="wait">
          <motion.div
            key={active}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.18, ease: 'easeOut' }}
          >
            <ActiveView />
          </motion.div>
        </AnimatePresence>

        <div className="h-28" />
      </div>

      <FloatingNav />
      <BookDetailSheet />
      <LoginSheet />
    </div>
  )
}
