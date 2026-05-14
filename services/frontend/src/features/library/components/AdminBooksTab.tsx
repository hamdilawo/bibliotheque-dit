import { useState } from 'react'
import { useAtom } from 'jotai'
import { booksAtom } from '../store'
import { Plus, Pencil, Trash2, X, Check } from 'lucide-react'
import { toast } from 'sonner'
import type { Book } from '../mock-data'

type EditState = Partial<Book> & { id?: string }

export function AdminBooksTab() {
  const [books, setBooks] = useAtom(booksAtom)
  const [search, setSearch] = useState('')
  const [editing, setEditing] = useState<EditState | null>(null)
  const [isNew, setIsNew] = useState(false)

  const filtered = books.filter(
    (b) =>
      b.title.toLowerCase().includes(search.toLowerCase()) ||
      b.author.toLowerCase().includes(search.toLowerCase())
  )

  const openNew = () => {
    setIsNew(true)
    setEditing({ title: '', author: '', genre: 'Informatique', available: 1, total: 1, description: '' })
  }

  const openEdit = (book: Book) => {
    setIsNew(false)
    setEditing({ ...book })
  }

  const handleSave = () => {
    if (!editing?.title || !editing?.author) return
    if (isNew) {
      const newBook: Book = {
        id: `b${Date.now()}`,
        title: editing.title!,
        author: editing.author!,
        genre: (editing.genre as Book['genre']) ?? 'Informatique',
        available: editing.available ?? 1,
        total: editing.total ?? 1,
        coverUrl: `https://picsum.photos/seed/${Date.now()}/120/176`,
        description: editing.description ?? '',
        pages: editing.pages ?? 200,
        year: editing.year ?? new Date().getFullYear(),
        borrowCount: 0,
        viewCount: 0,
      }
      setBooks([newBook, ...books])
      toast.success('Livre ajouté')
    } else {
      setBooks(books.map((b) => (b.id === editing.id ? { ...b, ...editing } as Book : b)))
      toast.success('Livre mis à jour')
    }
    setEditing(null)
  }

  const handleDelete = (id: string, title: string) => {
    setBooks(books.filter((b) => b.id !== id))
    toast.success(`"${title}" supprimé`)
  }

  return (
    <div className="px-5">
      {/* toolbar */}
      <div className="flex items-center gap-2 mb-4">
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Rechercher un livre..."
          className="flex-1 px-3 py-2 rounded-xl border border-border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/50"
        />
        <button
          onClick={openNew}
          className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-white text-sm font-semibold shadow-sm"
          style={{ backgroundColor: '#004455' }}
        >
          <Plus className="w-4 h-4" />
          Ajouter
        </button>
      </div>

      <p className="text-xs text-gray-400 mb-3">{filtered.length} livre{filtered.length > 1 ? 's' : ''}</p>

      <div className="space-y-2">
        {filtered.map((book) => (
          <div key={book.id} className="flex items-center gap-3 bg-white rounded-2xl border border-gray-100 p-3 shadow-sm">
            <img
              src={book.coverUrl}
              alt={book.title}
              className="w-10 h-14 object-cover rounded-lg flex-shrink-0"
              onError={(e) => { e.currentTarget.src = `https://picsum.photos/seed/${book.id}/80/112` }}
            />
            <div className="flex-1 min-w-0">
              <p className="font-semibold text-gray-900 text-sm line-clamp-1">{book.title}</p>
              <p className="text-gray-400 text-xs line-clamp-1">{book.author}</p>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-500">{book.genre}</span>
                <span className="text-xs text-gray-400">{book.available}/{book.total} dispo</span>
              </div>
            </div>
            <div className="flex items-center gap-1.5 flex-shrink-0">
              <button
                onClick={() => openEdit(book)}
                className="w-8 h-8 rounded-lg bg-gray-50 border border-gray-200 flex items-center justify-center hover:bg-blue-50 hover:border-blue-200 transition-colors"
              >
                <Pencil className="w-3.5 h-3.5 text-gray-500 hover:text-blue-500" />
              </button>
              <button
                onClick={() => handleDelete(book.id, book.title)}
                className="w-8 h-8 rounded-lg bg-gray-50 border border-gray-200 flex items-center justify-center hover:bg-red-50 hover:border-red-200 transition-colors"
              >
                <Trash2 className="w-3.5 h-3.5 text-gray-500 hover:text-red-500" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Edit / New sheet */}
      {editing && (
        <div className="fixed inset-0 z-50 flex flex-col justify-end">
          <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={() => setEditing(null)} />
          <div className="relative z-10 bg-card rounded-t-3xl border-t border-border px-6 pt-5 pb-10 shadow-2xl max-w-2xl w-full mx-auto">
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-lg font-semibold text-foreground">{isNew ? 'Ajouter un livre' : 'Modifier'}</h2>
              <button onClick={() => setEditing(null)} className="w-8 h-8 rounded-full bg-muted flex items-center justify-center">
                <X className="w-4 h-4 text-muted-foreground" />
              </button>
            </div>
            <div className="space-y-3">
              {[
                { label: 'Titre', key: 'title', type: 'text' },
                { label: 'Auteur', key: 'author', type: 'text' },
                { label: 'Pages', key: 'pages', type: 'number' },
                { label: 'Année', key: 'year', type: 'number' },
                { label: 'Exemplaires total', key: 'total', type: 'number' },
              ].map(({ label, key, type }) => (
                <div key={key}>
                  <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">{label}</label>
                  <input
                    type={type}
                    value={(editing as any)[key] ?? ''}
                    onChange={(e) => setEditing({ ...editing, [key]: type === 'number' ? Number(e.target.value) : e.target.value })}
                    className="mt-1 w-full px-3 py-2.5 rounded-xl border border-border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/30"
                  />
                </div>
              ))}
              <div>
                <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Description</label>
                <textarea
                  value={editing.description ?? ''}
                  onChange={(e) => setEditing({ ...editing, description: e.target.value })}
                  rows={2}
                  className="mt-1 w-full px-3 py-2.5 rounded-xl border border-border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 resize-none"
                />
              </div>
            </div>
            <button
              onClick={handleSave}
              className="mt-5 w-full flex items-center justify-center gap-2 rounded-full bg-primary py-2.5 text-sm font-medium text-primary-foreground shadow-sm hover:opacity-90"
            >
              <Check className="w-4 h-4" />
              {isNew ? 'Ajouter' : 'Enregistrer'}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
