import { useAtomValue } from 'jotai'
import { filteredBooksAtom, searchAtom, genreFilterAtom, isAuthenticatedAtom, currentUserAtom } from '../store'
import { SearchBar } from './SearchBar'
import { GenreChips } from './GenreChips'
import { RecommendationRow } from './RecommendationRow'
import { BookCard } from './BookCard'
import { BookOpen } from 'lucide-react'

export function DiscoverView() {
  const books = useAtomValue(filteredBooksAtom)
  const search = useAtomValue(searchAtom)
  const genre = useAtomValue(genreFilterAtom)
  const isFiltered = search || genre
  const isAuthenticated = useAtomValue(isAuthenticatedAtom)
  const currentUser = useAtomValue(currentUserAtom)

  const firstName = currentUser?.full_name?.split(' ')[0] ?? ''

  return (
    <div className="pb-6 space-y-5">
      <div className="px-5 pt-2">
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Bibliothèque DIT</p>
        <h1 className="text-2xl font-bold text-gray-900 mt-1 leading-snug">
          {isAuthenticated && firstName ? (
            <>
              Bienvenue,{' '}
              <span style={{ color: '#004455' }}>{firstName}</span> 👋
            </>
          ) : (
            <>Bienvenue 👋</>
          )}
        </h1>
      </div>

      <SearchBar />

      {!isFiltered && <RecommendationRow />}

      <GenreChips />

      <div className="px-5">
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-bold text-gray-900 text-sm">
            {isFiltered ? `Résultats (${books.length})` : 'Tous les livres'}
          </h2>
          <span className="text-xs text-gray-400">
            {books.length} livre{books.length > 1 ? 's' : ''}
          </span>
        </div>

        {books.length === 0 ? (
          <div className="text-center py-16">
            <BookOpen className="w-12 h-12 text-gray-200 mx-auto mb-3" />
            <p className="text-gray-400 font-semibold">Aucun livre trouvé</p>
            <p className="text-gray-300 text-sm mt-1">Essayez un autre terme</p>
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-3">
            {books.map((book) => (
              <BookCard key={book.id} book={book} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
