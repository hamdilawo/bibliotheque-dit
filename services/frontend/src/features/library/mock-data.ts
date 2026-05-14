import type { Loan } from './types'

function offset(days: number) {
  const d = new Date()
  d.setDate(d.getDate() + days)
  return d.toISOString()
}

export const LOANS: Loan[] = [
  { id: 'l1', bookId: 'b3',  borrowedAt: offset(-10), dueAt: offset(4),   returnedAt: null,        status: 'active' },
  { id: 'l2', bookId: 'b7',  borrowedAt: offset(-22), dueAt: offset(-8),  returnedAt: null,        status: 'overdue' },
  { id: 'l3', bookId: 'b12', borrowedAt: offset(-3),  dueAt: offset(11),  returnedAt: null,        status: 'active' },
  { id: 'l4', bookId: 'b4',  borrowedAt: offset(-45), dueAt: offset(-31), returnedAt: offset(-33), status: 'returned' },
  { id: 'l5', bookId: 'b1',  borrowedAt: offset(-60), dueAt: offset(-46), returnedAt: offset(-47), status: 'returned' },
]
