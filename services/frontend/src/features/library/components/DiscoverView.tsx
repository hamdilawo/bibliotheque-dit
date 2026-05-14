import { useAtomValue, useSetAtom } from 'jotai'
import { useEffect } from 'react'
import { filteredBooksAtom, searchAtom, genreFilterAtom, isAuthenticatedAtom, currentUserAtom, booksAtom, booksLoadingAtom, booksErrorAtom } from '../store'
import { SearchBar } from './SearchBar'
import { GenreChips } from './GenreChips'
import { RecommendationRow } from './RecommendationRow'
import { BookCard } from './BookCard'
import { BookOpen } from 'lucide-react'
import { fetchBooks } from '../api'

export function DiscoverView() {
  const books = useAtomValue(filteredBooksAtom)
  const search = useAtomValue(searchAtom)
  const genre = useAtomValue(genreFilterAtom)
  const isFiltered = search || genre
  const isAuthenticated = useAtomValue(isAuthenticatedAtom)
  const currentUser = useAtomValue(currentUserAtom)
  const setBooks = useSetAtom(booksAtom)
  const setLoading = useSetAtom(booksLoadingAtom)
  const setError = useSetAtom(booksErrorAtom)
  const loading = useAtomValue(booksLoadingAtom)
  const error = useAtomValue(booksErrorAtom)

  useEffect(() => {
    fetchBooks()
      .then((data) => { setBooks(data); setLoading(false) })
      .catch((e) => { setError(e.message); setLoading(false) })
  }, [])

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

        {loading ? (
          <div className="grid grid-cols-2 gap-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="rounded-2xl bg-gray-100 animate-pulse h-56" />
            ))}
          </div>
        ) : error ? (
          <div className="text-center py-16">
            <BookOpen className="w-12 h-12 text-gray-200 mx-auto mb-3" />
            <p className="text-gray-400 font-semibold">Service indisponible</p>
            <p className="text-gray-300 text-sm mt-1">{error}</p>
          </div>
        ) : books.length === 0 ? (
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
