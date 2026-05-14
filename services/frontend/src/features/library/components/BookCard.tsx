import { useSetAtom, useAtomValue } from 'jotai'
import { selectedBookAtom, borrowedBookIdsAtom } from '../store'
import type { Book } from '../mock-data'
import { Star, BookMarked } from 'lucide-react'
import { cn } from '@/lib/utils'

export function BookCard({ book }: { book: Book }) {
  const setSelected = useSetAtom(selectedBookAtom)
  const borrowedIds = useAtomValue(borrowedBookIdsAtom)
  const isBorrowed = borrowedIds.has(book.id)

  return (
    <button
      onClick={() => setSelected(book)}
      className="relative w-full rounded-2xl overflow-hidden group cursor-pointer active:scale-95 transition-transform duration-150"
    >
      <div className="relative h-56 overflow-hidden">
        <img
          src={book.coverUrl}
          alt={book.title}
          className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
          loading="lazy"
          onError={(e) => { e.currentTarget.src = `https://picsum.photos/seed/${book.id}/300/450` }}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/85 via-black/20 to-transparent" />

        {isBorrowed && (
          <div className="absolute top-2 left-2 flex items-center gap-1 px-2 py-0.5 rounded-full bg-[#004455]/90 text-white text-xs font-semibold">
            <BookMarked className="w-3 h-3" />
            Emprunté
          </div>
        )}

        <div
          className={cn(
            'absolute top-2 right-2 px-2 py-0.5 rounded-full text-xs font-semibold',
            book.available > 0 ? 'bg-emerald-500/90 text-white' : 'bg-rose-500/90 text-white'
          )}
        >
          {book.available > 0 ? `${book.available} dispo` : 'Indispo'}
        </div>

        <div className="absolute bottom-0 left-0 right-0 p-3">
          <p className="text-white font-semibold text-sm leading-tight line-clamp-2">{book.title}</p>
          <p className="text-white/65 text-xs mt-0.5 line-clamp-1">{book.author}</p>
          <div className="flex items-center gap-1 mt-1.5">
            <Star className="w-3 h-3 text-amber-400 fill-amber-400" />
            <span className="text-white/90 text-xs font-medium">{book.rating.toFixed(1)}</span>
            <span className="text-white/40 text-xs ml-1">{book.genre}</span>
          </div>
        </div>
      </div>
    </button>
  )
}
