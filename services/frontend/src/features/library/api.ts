import type { Book, Genre, Loan, LoanStatus } from './types'

const BOOKS_API = import.meta.env.VITE_BOOKS_API_URL ?? 'http://localhost:8003'
const LOANS_API = import.meta.env.VITE_LOANS_API_URL ?? 'http://localhost:8008'
const RECO_API = import.meta.env.VITE_RECOMMENDATION_API_URL ?? 'http://localhost:8004'

type ApiBookList = {
  id: string
  titre: string
  auteur: string
  isbn: string
  langue: string
  categorie_nom: string | null
  quantite_totale: number
  couverture_url: string
  couverture_url_publique: string
}

type ApiBookDetail = ApiBookList & {
  editeur: string
  annee_publication: number | null
  description: string
  nombre_pages: number | null
  actif: boolean
}

type PaginatedResponse = {
  count: number
  page: number
  page_size: number
  results: ApiBookList[]
}

function mapBook(api: ApiBookList): Book {
  return {
    id: String(api.id),
    title: api.titre,
    author: api.auteur,
    genre: (api.categorie_nom ?? 'Informatique') as Genre,
    description: '',
    coverUrl: api.couverture_url_publique || `https://picsum.photos/seed/${api.id}/300/450`,
    rating: 0,
    borrowCount: 0,
    viewCount: 0,
    available: api.quantite_totale,
    total: api.quantite_totale,
    year: 0,
    pages: 0,
  }
}

function mapBookDetail(api: ApiBookDetail): Book {
  return {
    ...mapBook(api),
    description: api.description ?? '',
    year: api.annee_publication ?? 0,
    pages: api.nombre_pages ?? 0,
  }
}

export async function fetchBooks(): Promise<Book[]> {
  const res = await fetch(`${BOOKS_API}/api/livres?page_size=100`)
  if (!res.ok) throw new Error('Erreur chargement livres')
  const data: PaginatedResponse = await res.json()
  return data.results.map(mapBook)
}

export async function fetchBookDetail(id: string): Promise<Book> {
  const res = await fetch(`${BOOKS_API}/api/livres/${id}`)
  if (!res.ok) throw new Error('Livre introuvable')
  const data: ApiBookDetail = await res.json()
  return mapBookDetail(data)
}

export async function searchBooks(q: string): Promise<Book[]> {
  const res = await fetch(`${BOOKS_API}/api/livres/search?q=${encodeURIComponent(q)}&page_size=100`)
  if (!res.ok) throw new Error('Erreur recherche')
  const data: PaginatedResponse = await res.json()
  return data.results.map(mapBook)
}

export async function createBook(fields: {
  titre: string; auteur: string; isbn: string; description?: string
  nombre_pages?: number; annee_publication?: number; quantite_totale?: number
  couverture?: File
}, token: string): Promise<Book> {
  const form = new FormData()
  Object.entries(fields).forEach(([k, v]) => {
    if (v === undefined) return
    if (v instanceof File) form.append(k, v)
    else form.append(k, String(v))
  })
  const res = await fetch(`${BOOKS_API}/api/livres`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
    body: form,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail ?? 'Erreur création')
  }
  return mapBookDetail(await res.json())
}

export async function updateBook(id: string, fields: {
  titre?: string; auteur?: string; description?: string
  nombre_pages?: number; annee_publication?: number; quantite_totale?: number
}, token: string): Promise<Book> {
  const res = await fetch(`${BOOKS_API}/api/livres/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify(fields),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail ?? 'Erreur modification')
  }
  return mapBookDetail(await res.json())
}

export async function deleteBook(id: string, token: string): Promise<void> {
  const res = await fetch(`${BOOKS_API}/api/livres/${id}`, {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!res.ok) throw new Error('Erreur suppression')
}

// ── Emprunts ────────────────────────────────────────────────────────────────

type ApiLoan = {
  id: string
  utilisateur_id: string
  livre_id: string
  date_emprunt: string
  date_retour_prevue: string
  date_retour_effective: string | null
  statut: string
}

function mapLoan(api: ApiLoan): Loan {
  let status: LoanStatus = 'active'
  // Le domaine Python utilise "completed" (pas "RETOURNE")
  if (api.statut === 'completed' || api.statut === 'RETOURNE') {
    status = 'returned'
  } else if (
    api.statut === 'EN_RETARD' ||
    (api.date_retour_prevue && new Date(api.date_retour_prevue) < new Date())
  ) {
    status = 'overdue'
  }
  return {
    id: String(api.id),
    bookId: String(api.livre_id),
    borrowedAt: api.date_emprunt,
    dueAt: api.date_retour_prevue,
    returnedAt: api.date_retour_effective ?? null,
    status,
  }
}

export async function fetchMyLoans(token: string, _userId?: string): Promise<Loan[]> {
  const res = await fetch(`${LOANS_API}/api/emprunts/`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!res.ok) throw new Error('Erreur chargement emprunts')
  const data = await res.json()
  const results: ApiLoan[] = data.results ?? []
  return results.map(mapLoan)
}

export async function borrowBook(bookId: string, token: string): Promise<string> {
  const res = await fetch(`${LOANS_API}/api/emprunts/emprunter/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify({ book_id: bookId }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.error ?? 'Erreur emprunt')
  }
  const data = await res.json()
  return String(data.data?.loan_id ?? '')
}

export async function returnBook(loanId: string, token: string): Promise<void> {
  const res = await fetch(`${LOANS_API}/api/emprunts/retourner/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify({ loan_id: loanId }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.error ?? 'Erreur retour')
  }
}

// ── Recommandations ─────────────────────────────────────────────────────────

type ApiRecoItem = {
  livre_id: number | null
  score: number
  titre: string | null
  auteur: string | null
  isbn: string | null
  disponible: boolean | null
  categorie: string | null
}

function mapRecoItem(item: ApiRecoItem, allBooks: Book[]): Book | null {
  const found = allBooks.find((b) => b.id === String(item.livre_id))
  if (found) return { ...found, rating: parseFloat(Math.min(5, Math.abs(item.score) * 3 + 3.5).toFixed(1)) }
  if (!item.titre) return null
  return {
    id: String(item.livre_id ?? item.isbn ?? ''),
    title: item.titre,
    author: item.auteur ?? '',
    genre: (item.categorie ?? 'Informatique') as Genre,
    description: '',
    coverUrl: `https://picsum.photos/seed/${item.isbn ?? item.livre_id}/300/450`,
    rating: 4.0,
    borrowCount: 0,
    viewCount: 0,
    available: item.disponible ? 1 : 0,
    total: 1,
    year: 0,
    pages: 0,
  }
}

export async function fetchRecommendations(userId: string, allBooks: Book[]): Promise<Book[]> {
  const res = await fetch(`${RECO_API}/recommendations/${userId}`)
  if (!res.ok) throw new Error(`Service recommandation indisponible (${res.status})`)
  const data = await res.json()
  const items: ApiRecoItem[] = data.recommandations ?? []
  return items
    .map((item) => mapRecoItem(item, allBooks))
    .filter((b): b is Book => b !== null)
}

export async function fetchPopularBooks(allBooks: Book[]): Promise<Book[]> {
  try {
    const res = await fetch(`${RECO_API}/popular?n=8`)
    if (!res.ok) throw new Error()
    const data = await res.json()
    const top: { livre_id: string | null }[] = data.top_livres ?? []
    const result = top
      .map((item) => allBooks.find((b) => b.id === String(item.livre_id)))
      .filter((b): b is Book => b !== undefined)
    if (result.length > 0) return result
  } catch {}
  // fallback : premiers livres du catalogue
  return allBooks.slice(0, 8)
}
