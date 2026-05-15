import { atom } from 'jotai'
import { atomWithStorage } from 'jotai/utils'
import type { Book, Loan } from './types'

export const activeViewAtom = atom<'discover' | 'loans' | 'account' | 'admin'>('discover')

export const adminTabAtom = atom<'books' | 'loans' | 'users' | null>(null)

export const selectedBookAtom = atom<Book | null>(null)

export const searchAtom = atom('')

export const genreFilterAtom = atom<string | null>(null)

export const booksAtom = atom<Book[]>([])
export const booksLoadingAtom = atom(true)
export const booksErrorAtom = atom<string | null>(null)

export const loansAtom = atom<Loan[]>([])

const GENRE_PRIORITY: Record<string, number> = {
  'Data Engineering': 0,
  'Data Science': 1,
  'Intelligence Artificielle': 2,
  'Informatique': 3,
  'Mathématiques': 4,
  'Sciences': 5,
  'Littérature': 6,
}

export const filteredBooksAtom = atom((get) => {
  const books = get(booksAtom)
  const search = get(searchAtom).toLowerCase().trim()
  const genre = get(genreFilterAtom)
  const filtered = books.filter((b) => {
    const matchSearch =
      !search ||
      b.title.toLowerCase().includes(search) ||
      b.author.toLowerCase().includes(search)
    const matchGenre = !genre || b.genre === genre
    return matchSearch && matchGenre
  })
  if (search || genre) return filtered
  return [...filtered].sort(
    (a, b) => (GENRE_PRIORITY[a.genre] ?? 99) - (GENRE_PRIORITY[b.genre] ?? 99)
  )
})

export const recommendedBooksAtom = atom<Book[]>([])

export const activeLoansAtom = atom((get) =>
  get(loansAtom).filter((l) => l.status === 'active' || l.status === 'overdue')
)

export const borrowedBookIdsAtom = atom((get) =>
  new Set(get(activeLoansAtom).map((l) => l.bookId))
)

export const isAuthenticatedAtom = atomWithStorage('auth', false)

export const currentUserAtom = atomWithStorage<{
  id: string
  email: string
  full_name: string
  role: string
} | null>('currentUser', null)

export const accessTokenAtom = atomWithStorage<string | null>('accessToken', null)

export const loginSheetOpenAtom = atom(false)
