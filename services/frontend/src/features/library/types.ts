export type Genre = string

export type Book = {
  id: string
  title: string
  author: string
  genre: Genre
  description: string
  coverUrl: string
  rating: number
  borrowCount: number
  viewCount: number
  available: number
  total: number
  year: number
  pages: number
}

export type LoanStatus = 'active' | 'overdue' | 'returned'

export type Loan = {
  id: string
  bookId: string
  borrowedAt: string
  dueAt: string
  returnedAt: string | null
  status: LoanStatus
}
