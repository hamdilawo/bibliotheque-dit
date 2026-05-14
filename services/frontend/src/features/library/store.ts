import { atom } from 'jotai'
import { BOOKS, LOANS, type Book, type Loan } from './mock-data'

export const activeViewAtom = atom<'discover' | 'loans' | 'account' | 'admin'>('discover')

export const adminTabAtom = atom<'books' | 'loans' | 'users' | null>(null)

export const selectedBookAtom = atom<Book | null>(null)

export const searchAtom = atom('')

export const genreFilterAtom = atom<string | null>(null)

export const booksAtom = atom<Book[]>([...BOOKS])

export const loansAtom = atom<Loan[]>(LOANS)

export const filteredBooksAtom = atom((get) => {
  const books = get(booksAtom)
  const search = get(searchAtom).toLowerCase().trim()
  const genre = get(genreFilterAtom)
  return books.filter((b) => {
    const matchSearch =
      !search ||
      b.title.toLowerCase().includes(search) ||
      b.author.toLowerCase().includes(search)
    const matchGenre = !genre || b.genre === genre
    return matchSearch && matchGenre
  })
})

export const recommendedBooksAtom = atom((get) =>
  [...get(booksAtom)]
    .sort((a, b) => b.borrowCount + b.viewCount - (a.borrowCount + a.viewCount))
    .slice(0, 8)
)

export const activeLoansAtom = atom((get) =>
  get(loansAtom).filter((l) => l.status === 'active' || l.status === 'overdue')
)

export const borrowedBookIdsAtom = atom((get) =>
  new Set(get(activeLoansAtom).map((l) => l.bookId))
)

export const isAuthenticatedAtom = atom(false)

export const currentUserAtom = atom<{
  id: string
  email: string
  full_name: string
  role: string
} | null>(null)

export const loginSheetOpenAtom = atom(false)
