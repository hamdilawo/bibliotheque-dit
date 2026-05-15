import { useEffect, useState } from 'react'
import { useAtom, useAtomValue } from 'jotai'
import { recommendedBooksAtom, selectedBookAtom, isAuthenticatedAtom, currentUserAtom, booksAtom } from '../store'
import { fetchRecommendations, fetchPopularBooks } from '../api'
import { Star, TrendingUp, Sparkles } from 'lucide-react'

export function RecommendationRow() {
  const [recommended, setRecommended] = useAtom(recommendedBooksAtom)
  const setSelected = useAtom(selectedBookAtom)[1]
  const isAuthenticated = useAtomValue(isAuthenticatedAtom)
  const currentUser = useAtomValue(currentUserAtom)
  const allBooks = useAtomValue(booksAtom)
  const [loading, setLoading] = useState(true)
  const [isPersonalized, setIsPersonalized] = useState(false)

  useEffect(() => {
    if (allBooks.length === 0) return

    setLoading(true)
    setIsPersonalized(false)

    const load = async () => {
      if (isAuthenticated && currentUser?.id) {
        try {
          const recos = await fetchRecommendations(currentUser.id, allBooks)
          if (recos.length > 0) {
            setRecommended(recos)
            setIsPersonalized(true)
            return
          }
        } catch {}
      }
      // fallback : livres populaires ou catalogue
      const popular = await fetchPopularBooks(allBooks)
      setRecommended(popular)
    }

    load().finally(() => setLoading(false))
  }, [isAuthenticated, currentUser?.id, allBooks.length])

  if (!loading && recommended.length === 0) return null

  return (
    <section>
      <div className="flex items-center gap-2 px-5 mb-3">
        {isPersonalized ? (
          <Sparkles className="w-4 h-4" style={{ color: '#004455' }} />
        ) : (
          <TrendingUp className="w-4 h-4" style={{ color: '#004455' }} />
        )}
        <h2 className="font-bold text-gray-900 text-sm">
          {isPersonalized ? 'Pour vous' : 'Les plus populaires'}
        </h2>
        {isPersonalized && (
          <span className="text-xs text-gray-400">· Basé sur vos emprunts</span>
        )}
      </div>

      <div
        className="flex gap-3 overflow-x-auto px-5 pb-2"
        style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' } as React.CSSProperties}
      >
        {loading
          ? Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="flex-shrink-0 w-[120px]">
                <div className="h-44 rounded-xl bg-gray-100 animate-pulse" />
                <div className="h-3 rounded mt-2 bg-gray-100 animate-pulse w-3/4" />
                <div className="h-3 rounded mt-1 bg-gray-100 animate-pulse w-1/2" />
              </div>
            ))
          : recommended.map((book) => (
              <button
                key={book.id}
                onClick={() => setSelected(book)}
                className="flex-shrink-0 w-[120px] group active:scale-95 transition-transform duration-150 text-left"
              >
                <div className="relative h-44 rounded-xl overflow-hidden">
                  <img
                    src={book.coverUrl}
                    alt={book.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    loading="lazy"
                    onError={(e) => { e.currentTarget.src = `https://picsum.photos/seed/${book.id}/120/176` }}
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent" />
                  {book.rating > 0 && (
                    <div className="absolute bottom-2 left-2 flex items-center gap-0.5">
                      <Star className="w-3 h-3 text-amber-400 fill-amber-400" />
                      <span className="text-white text-xs font-semibold">{book.rating.toFixed(1)}</span>
                    </div>
                  )}
                </div>
                <p className="text-xs font-semibold text-gray-800 mt-2 leading-tight line-clamp-2">{book.title}</p>
                <p className="text-xs text-gray-500 line-clamp-1 mt-0.5">{book.author}</p>
              </button>
            ))}
      </div>
    </section>
  )
}
