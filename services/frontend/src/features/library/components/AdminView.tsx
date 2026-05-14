import { useAtom } from 'jotai'
import { adminTabAtom } from '../store'
import { AnimatePresence, motion } from 'framer-motion'
import { ArrowLeft } from 'lucide-react'
import { AdminBooksTab } from './AdminBooksTab'
import { AdminLoansTab } from './AdminLoansTab'
import { AdminUsersTab } from './AdminUsersTab'

const CARDS = [
  {
    id: 'books' as const,
    label: 'Livres',
    description: 'Gérer le catalogue — ajouter, modifier, supprimer',
    gradient: 'from-[#004455] to-[#006e8a]',
    blob1: 'bg-white/10',
    blob2: 'bg-teal-300/20',
    svg: (
      <svg viewBox="0 0 80 80" fill="none" className="w-full h-full">
        <rect x="14" y="12" width="32" height="46" rx="4" fill="white" fillOpacity="0.15" />
        <rect x="14" y="12" width="32" height="46" rx="4" stroke="white" strokeOpacity="0.5" strokeWidth="2" />
        <rect x="20" y="22" width="20" height="2.5" rx="1.25" fill="white" fillOpacity="0.7" />
        <rect x="20" y="29" width="14" height="2.5" rx="1.25" fill="white" fillOpacity="0.5" />
        <rect x="20" y="36" width="17" height="2.5" rx="1.25" fill="white" fillOpacity="0.5" />
        <rect x="34" y="16" width="28" height="46" rx="4" fill="white" fillOpacity="0.25" />
        <rect x="34" y="16" width="28" height="46" rx="4" stroke="white" strokeOpacity="0.7" strokeWidth="2" />
        <rect x="40" y="26" width="16" height="2.5" rx="1.25" fill="white" fillOpacity="0.9" />
        <rect x="40" y="33" width="11" height="2.5" rx="1.25" fill="white" fillOpacity="0.65" />
        <rect x="40" y="40" width="14" height="2.5" rx="1.25" fill="white" fillOpacity="0.65" />
        <rect x="40" y="47" width="9" height="2.5" rx="1.25" fill="white" fillOpacity="0.5" />
      </svg>
    ),
  },
  {
    id: 'loans' as const,
    label: 'Emprunts',
    description: 'Suivre les emprunts, gérer les retards',
    gradient: 'from-[#3730a3] to-[#6d28d9]',
    blob1: 'bg-indigo-300/20',
    blob2: 'bg-purple-300/20',
    svg: (
      <svg viewBox="0 0 80 80" fill="none" className="w-full h-full">
        <rect x="12" y="18" width="44" height="48" rx="6" fill="white" fillOpacity="0.15" stroke="white" strokeOpacity="0.5" strokeWidth="2" />
        <rect x="22" y="12" width="6" height="14" rx="3" fill="white" fillOpacity="0.8" />
        <rect x="40" y="12" width="6" height="14" rx="3" fill="white" fillOpacity="0.8" />
        <rect x="12" y="30" width="44" height="2" fill="white" fillOpacity="0.3" />
        <rect x="20" y="39" width="8" height="8" rx="2" fill="white" fillOpacity="0.6" />
        <rect x="33" y="39" width="8" height="8" rx="2" fill="white" fillOpacity="0.3" />
        <rect x="46" y="39" width="8" height="8" rx="2" fill="white" fillOpacity="0.3" />
        <rect x="20" y="52" width="8" height="8" rx="2" fill="white" fillOpacity="0.3" />
        <circle cx="60" cy="58" r="12" fill="#ef4444" fillOpacity="0.9" />
        <rect x="59" y="52" width="2" height="7" rx="1" fill="white" />
        <rect x="59" y="61" width="2" height="2" rx="1" fill="white" />
      </svg>
    ),
  },
  {
    id: 'users' as const,
    label: 'Utilisateurs',
    description: 'Inviter et gérer les membres DIT',
    gradient: 'from-[#92400e] to-[#b45309]',
    blob1: 'bg-amber-300/20',
    blob2: 'bg-orange-300/20',
    svg: (
      <svg viewBox="0 0 80 80" fill="none" className="w-full h-full">
        <circle cx="34" cy="26" r="10" fill="white" fillOpacity="0.25" stroke="white" strokeOpacity="0.6" strokeWidth="2" />
        <path d="M14 60c0-11 9-18 20-18s20 7 20 18" stroke="white" strokeOpacity="0.6" strokeWidth="2" strokeLinecap="round" />
        <circle cx="58" cy="30" r="7" fill="white" fillOpacity="0.15" stroke="white" strokeOpacity="0.4" strokeWidth="1.5" />
        <path d="M46 56c0-7.7 5.4-13 12-13" stroke="white" strokeOpacity="0.4" strokeWidth="1.5" strokeLinecap="round" />
        <circle cx="62" cy="54" r="10" fill="white" fillOpacity="0.9" />
        <rect x="61" y="49" width="2" height="10" rx="1" fill="#b45309" />
        <rect x="57" y="53" width="10" height="2" rx="1" fill="#b45309" />
      </svg>
    ),
  },
]

const PANELS = {
  books: AdminBooksTab,
  loans: AdminLoansTab,
  users: AdminUsersTab,
}

export function AdminView() {
  const [tab, setTab] = useAtom(adminTabAtom)
  const Panel = tab ? PANELS[tab] : null
  const current = tab ? CARDS.find((c) => c.id === tab) : null

  return (
    <div className="pb-6 min-h-screen">
      <AnimatePresence mode="wait">
        {!tab ? (
          <motion.div
            key="dashboard"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.18 }}
          >
            <div className="px-5 pt-2 mb-6">
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Administration</p>
              <h1 className="text-2xl font-bold text-gray-900 mt-1">Tableau de bord</h1>
            </div>

            <div className="px-5 space-y-4">
              {CARDS.map((card, i) => (
                <motion.button
                  key={card.id}
                  onClick={() => setTab(card.id)}
                  className={`w-full text-left relative overflow-hidden rounded-3xl bg-gradient-to-br ${card.gradient} p-6 shadow-lg active:scale-[0.98] transition-transform`}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.07, duration: 0.25 }}
                >
                  {/* blobs */}
                  <div className={`pointer-events-none absolute -top-8 -right-8 w-36 h-36 rounded-full ${card.blob1} blur-2xl`} />
                  <div className={`pointer-events-none absolute -bottom-10 -left-6 w-40 h-40 rounded-full ${card.blob2} blur-2xl`} />

                  <div className="relative z-10 flex items-center gap-5">
                    <div className="w-16 h-16 flex-shrink-0">
                      {card.svg}
                    </div>
                    <div>
                      <p className="text-white font-bold text-lg leading-tight">{card.label}</p>
                      <p className="text-white/65 text-sm mt-0.5 leading-snug">{card.description}</p>
                    </div>
                    <div className="ml-auto">
                      <ArrowLeft className="w-5 h-5 text-white/50 rotate-180" />
                    </div>
                  </div>
                </motion.button>
              ))}
            </div>
          </motion.div>
        ) : (
          <motion.div
            key={tab}
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.2 }}
          >
            {/* sub-header */}
            <div className="px-5 pt-2 mb-5 flex items-center gap-3">
              <button
                onClick={() => setTab(null)}
                className="w-8 h-8 rounded-xl bg-white border border-gray-200 flex items-center justify-center shadow-sm hover:bg-gray-50 transition-colors"
              >
                <ArrowLeft className="w-4 h-4 text-gray-600" />
              </button>
              <div>
                <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Administration</p>
                <h1 className="text-xl font-bold text-gray-900 leading-tight">{current?.label}</h1>
              </div>
            </div>

            {Panel && <Panel />}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
