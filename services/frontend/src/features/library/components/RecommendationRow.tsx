import { useAtomValue, useSetAtom } from 'jotai'
import { recommendedBooksAtom, selectedBookAtom } from '../store'
import { Star, TrendingUp } from 'lucide-react'

export function RecommendationRow() {
  const recommended = useAtomValue(recommendedBooksAtom)
  const setSelected = useSetAtom(selectedBookAtom)

  return (
    <section>
      <div className="flex items-center gap-2 px-5 mb-3">
        <TrendingUp className="w-4 h-4" style={{ color: '#004455' }} />
        <h2 className="font-bold text-gray-900 text-sm">Pour vous</h2>
        <span className="text-xs text-gray-400">· Les plus populaires</span>
      </div>
      <div
        className="flex gap-3 overflow-x-auto px-5 pb-2"
        style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' } as React.CSSProperties}
      >
        {recommended.map((book) => (
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
              <div className="absolute bottom-2 left-2 flex items-center gap-0.5">
                <Star className="w-3 h-3 text-amber-400 fill-amber-400" />
                <span className="text-white text-xs font-semibold">{book.rating.toFixed(1)}</span>
              </div>
            </div>
            <p className="text-xs font-semibold text-gray-800 mt-2 leading-tight line-clamp-2">{book.title}</p>
            <p className="text-xs text-gray-500 line-clamp-1 mt-0.5">{book.author}</p>
          </button>
        ))}
      </div>
    </section>
  )
}
