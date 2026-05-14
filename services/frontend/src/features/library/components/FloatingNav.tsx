import { useAtom, useAtomValue } from 'jotai'
import { activeViewAtom, isAuthenticatedAtom, currentUserAtom } from '../store'
import { BookOpen, BookMarked, User, LayoutDashboard } from 'lucide-react'
import { cn } from '@/lib/utils'
import { motion } from 'framer-motion'

const NAV = [
  { id: 'discover', label: 'Découvrir', Icon: BookOpen },
  { id: 'loans',    label: 'Emprunts',  Icon: BookMarked },
  { id: 'account',  label: 'Compte',    Icon: User },
] as const

export function FloatingNav() {
  const [active, setActive] = useAtom(activeViewAtom)
  const isAuthenticated = useAtomValue(isAuthenticatedAtom)
  const currentUser = useAtomValue(currentUserAtom)
  const isAdmin = isAuthenticated && currentUser?.role === 'STAFF'

  return (
    <div className="fixed bottom-6 left-0 right-0 flex justify-center z-30 pointer-events-none">
      <motion.div
        className="flex items-center gap-1 px-2 py-2 rounded-full bg-white/90 backdrop-blur-xl shadow-2xl shadow-black/20 border border-white/60 pointer-events-auto"
        initial={{ y: 80, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ type: 'spring', damping: 22, stiffness: 260, delay: 0.2 }}
      >
        {NAV.map(({ id, label, Icon }) => {
          const isActive = active === id
          return (
            <button
              key={id}
              onClick={() => setActive(id as any)}
              className={cn(
                'flex items-center gap-2 px-4 py-2.5 rounded-full transition-all duration-200 active:scale-95',
                isActive ? 'text-white shadow-sm' : 'text-gray-400 hover:text-gray-600 hover:bg-gray-50'
              )}
              style={isActive ? { backgroundColor: '#004455' } : undefined}
            >
              <Icon className="w-4 h-4 flex-shrink-0" />
              {isActive && (
                <motion.span
                  className="text-xs font-semibold whitespace-nowrap overflow-hidden"
                  initial={{ opacity: 0, maxWidth: 0 }}
                  animate={{ opacity: 1, maxWidth: 80 }}
                  transition={{ duration: 0.2 }}
                >
                  {label}
                </motion.span>
              )}
            </button>
          )
        })}

        {isAdmin && (
          <button
            onClick={() => setActive('admin')}
            className={cn(
              'flex items-center gap-2 px-4 py-2.5 rounded-full transition-all duration-200 active:scale-95',
              active === 'admin' ? 'text-white shadow-sm' : 'text-gray-400 hover:text-gray-600 hover:bg-gray-50'
            )}
            style={active === 'admin' ? { backgroundColor: '#004455' } : undefined}
          >
            <LayoutDashboard className="w-4 h-4 flex-shrink-0" />
            {active === 'admin' && (
              <motion.span
                className="text-xs font-semibold whitespace-nowrap overflow-hidden"
                initial={{ opacity: 0, maxWidth: 0 }}
                animate={{ opacity: 1, maxWidth: 80 }}
                transition={{ duration: 0.2 }}
              >
                Admin
              </motion.span>
            )}
          </button>
        )}
      </motion.div>
    </div>
  )
}
