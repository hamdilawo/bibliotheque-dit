import { useAtom, useAtomValue } from 'jotai'
import { useEffect, useState } from 'react'
import { selectedBookAtom, loansAtom, booksAtom, borrowedBookIdsAtom, accessTokenAtom, currentUserAtom } from '../store'
import { AnimatePresence, motion } from 'framer-motion'
import { X, Star, BookOpen, Clock, Users, Download, TrendingUp, Loader2 } from 'lucide-react'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'
import { fetchBookDetail, borrowBook, returnBook, fetchMyLoans } from '../api'

const GENRE_COLORS: Record<string, string> = {
  'Data Engineering': '#0f766e',
  'Data Science': '#0284c7',
  'Informatique': '#0369a1',
  'Intelligence Artificielle': '#7c3aed',
  'Mathématiques': '#9333ea',
  'Sciences': '#059669',
  'Littérature': '#b45309',
}

export function BookDetailSheet() {
  const [book, setBook] = useAtom(selectedBookAtom)
  const [loans, setLoans] = useAtom(loansAtom)
  const [books, setBooks] = useAtom(booksAtom)
  const borrowedIds = useAtomValue(borrowedBookIdsAtom)
  const token = useAtomValue(accessTokenAtom)
  const currentUser = useAtomValue(currentUserAtom)
  const [busy, setBusy] = useState(false)

  const isBorrowed = book ? borrowedIds.has(book.id) : false

  useEffect(() => {
    if (!book) return
    fetchBookDetail(book.id).then((full) => setBook(full)).catch(() => {})
  }, [book?.id])

  const handleBorrow = async () => {
    if (!book) return
    if (!token || !currentUser) {
      toast.error('Connectez-vous pour emprunter un livre')
      return
    }
    setBusy(true)
    try {
      await borrowBook(book.id, token)
      const fresh = await fetchMyLoans(token, currentUser.id)
      setLoans(fresh)
      setBooks(books.map((b) => (b.id === book.id ? { ...b, available: Math.max(0, b.available - 1) } : b)))
      toast.success('Livre emprunté !', { description: `"${book.title}" · À rendre dans 14 jours` })
      setBook(null)
    } catch (e: any) {
      toast.error(e.message)
    } finally {
      setBusy(false)
    }
  }

  const handleReturn = async () => {
    if (!book || !token || !currentUser) return
    const activeLoan = loans.find((l) => l.bookId === book.id && l.status !== 'returned')
    if (!activeLoan) return
    setBusy(true)
    try {
      await returnBook(activeLoan.id, token)
      const fresh = await fetchMyLoans(token, currentUser.id)
      setLoans(fresh)
      setBooks(books.map((b) => (b.id === book.id ? { ...b, available: b.available + 1 } : b)))
      toast.success('Livre rendu !', { description: `"${book.title}" a été retourné` })
      setBook(null)
    } catch (e: any) {
      toast.error(e.message)
    } finally {
      setBusy(false)
    }
  }

  const genreColor = book ? (GENRE_COLORS[book.genre] ?? '#004455') : '#004455'

  return (
    <AnimatePresence>
      {book && (
        <>
          <motion.div
            className="fixed inset-0 bg-black/60 z-40 backdrop-blur-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setBook(null)}
          />
          <motion.div
            className="fixed bottom-0 left-0 right-0 z-50 bg-white rounded-t-3xl max-h-[92vh] overflow-hidden flex flex-col"
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
          >
            {/* Drag handle */}
            <div className="flex justify-center pt-3 pb-1 flex-shrink-0">
              <div className="w-10 h-1 rounded-full bg-gray-200" />
            </div>

            <div className="overflow-y-auto flex-1 pb-32">

              {/* ── Hero ── */}
              <div className="relative h-52 mx-4 mt-2 rounded-2xl overflow-hidden">
                {/* Blurred cover background */}
                <img
                  src={book.coverUrl}
                  alt=""
                  aria-hidden
                  className="absolute inset-0 w-full h-full object-cover"
                  style={{ filter: 'blur(18px)', transform: 'scale(1.25)' }}
                  onError={(e) => { e.currentTarget.src = `https://picsum.photos/seed/${book.id}/300/450` }}
                />
                <div className="absolute inset-0 bg-black/55" />

                {/* Close */}
                <button
                  onClick={() => setBook(null)}
                  className="absolute top-3 right-3 w-8 h-8 rounded-full bg-black/30 backdrop-blur-sm flex items-center justify-center z-10 cursor-pointer"
                >
                  <X className="w-4 h-4 text-white" />
                </button>

                {/* Cover card + meta */}
                <div className="absolute inset-0 flex items-end px-4 pb-4 gap-4">
                  <div className="w-[88px] h-[132px] rounded-xl overflow-hidden shadow-2xl flex-shrink-0 border-2 border-white/25">
                    <img
                      src={book.coverUrl}
                      alt={book.title}
                      className="w-full h-full object-cover"
                      onError={(e) => { e.currentTarget.src = `https://picsum.photos/seed/${book.id}/300/450` }}
                    />
                  </div>

                  <div className="flex-1 min-w-0 pb-1">
                    <span
                      className="inline-block text-xs font-semibold px-2.5 py-0.5 rounded-full mb-2"
                      style={{
                        backgroundColor: `${genreColor}30`,
                        color: genreColor,
                        border: `1px solid ${genreColor}50`,
                      }}
                    >
                      {book.genre}
                    </span>
                    <h2 className="text-white font-bold text-lg leading-snug line-clamp-2">{book.title}</h2>
                    <p className="text-white/65 text-sm mt-1 line-clamp-1">{book.author}</p>
                    <div className="flex items-center gap-0.5 mt-2">
                      {Array.from({ length: 5 }).map((_, i) => (
                        <Star
                          key={i}
                          className={cn(
                            'w-3.5 h-3.5',
                            i < Math.round(book.rating)
                              ? 'text-amber-400 fill-amber-400'
                              : 'text-white/25 fill-white/10'
                          )}
                        />
                      ))}
                      <span className="text-white/80 text-xs font-semibold ml-1.5">{book.rating.toFixed(1)}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* ── Quick stat chips ── */}
              <div
                className="flex gap-2 px-4 mt-4 overflow-x-auto"
                style={{ scrollbarWidth: 'none' } as React.CSSProperties}
              >
                <div className="flex items-center gap-1.5 bg-gray-50 border border-gray-100 rounded-full px-3 py-1.5 flex-shrink-0">
                  <BookOpen className="w-3.5 h-3.5 text-gray-400" />
                  <span className="text-xs text-gray-600 font-medium">{book.pages} pages</span>
                </div>
                <div className="flex items-center gap-1.5 bg-gray-50 border border-gray-100 rounded-full px-3 py-1.5 flex-shrink-0">
                  <Clock className="w-3.5 h-3.5 text-gray-400" />
                  <span className="text-xs text-gray-600 font-medium">{book.year}</span>
                </div>
                <div className="flex items-center gap-1.5 bg-gray-50 border border-gray-100 rounded-full px-3 py-1.5 flex-shrink-0">
                  <Users className="w-3.5 h-3.5 text-gray-400" />
                  <span className={cn('text-xs font-semibold', book.available > 0 ? 'text-emerald-600' : 'text-rose-500')}>
                    {book.available}/{book.total} exemplaires
                  </span>
                </div>
              </div>

              {/* ── Description ── */}
              <div className="px-4 mt-5">
                <h3 className="text-sm font-bold text-gray-900 mb-2">À propos</h3>
                <p className="text-gray-500 text-sm leading-relaxed">{book.description}</p>
              </div>

              {/* ── Stats cards ── */}
              <div className="grid grid-cols-2 gap-3 px-4 mt-5">
                <div className="rounded-2xl p-4 flex items-center gap-3" style={{ backgroundColor: '#00445509' }}>
                  <div className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0" style={{ backgroundColor: '#00445520' }}>
                    <Download className="w-4 h-4" style={{ color: '#004455' }} />
                  </div>
                  <div>
                    <p className="text-xl font-bold leading-none" style={{ color: '#004455' }}>{book.borrowCount}</p>
                    <p className="text-xs text-gray-400 mt-0.5">Emprunts</p>
                  </div>
                </div>
                <div className="rounded-2xl p-4 flex items-center gap-3" style={{ backgroundColor: '#00445509' }}>
                  <div className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0" style={{ backgroundColor: '#00445520' }}>
                    <TrendingUp className="w-4 h-4" style={{ color: '#004455' }} />
                  </div>
                  <div>
                    <p className="text-xl font-bold leading-none" style={{ color: '#004455' }}>{book.viewCount}</p>
                    <p className="text-xs text-gray-400 mt-0.5">Consultations</p>
                  </div>
                </div>
              </div>

            </div>

            {/* ── CTA ── */}
            <div className="absolute bottom-0 left-0 right-0 p-5 bg-white/95 backdrop-blur-sm border-t border-gray-100">
              {isBorrowed ? (
                <button
                  onClick={handleReturn}
                  disabled={busy}
                  className="w-full py-4 rounded-2xl bg-gray-100 text-gray-700 font-semibold text-base active:scale-[0.98] transition-transform cursor-pointer disabled:opacity-60 flex items-center justify-center gap-2"
                >
                  {busy && <Loader2 className="w-4 h-4 animate-spin" />}
                  Rendre ce livre
                </button>
              ) : book.available > 0 ? (
                <button
                  onClick={handleBorrow}
                  disabled={busy}
                  className="w-full py-4 rounded-2xl text-white font-semibold text-base active:scale-[0.98] transition-transform cursor-pointer disabled:opacity-60 flex items-center justify-center gap-2"
                  style={{ backgroundColor: '#004455' }}
                >
                  {busy && <Loader2 className="w-4 h-4 animate-spin" />}
                  Emprunter · 14 jours
                </button>
              ) : (
                <button
                  disabled
                  className="w-full py-4 rounded-2xl bg-gray-100 text-gray-400 font-semibold text-base cursor-not-allowed"
                >
                  Aucun exemplaire disponible
                </button>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
