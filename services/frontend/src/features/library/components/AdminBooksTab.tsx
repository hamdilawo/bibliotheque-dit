import { useState, useRef } from 'react'
import { useAtom, useAtomValue } from 'jotai'
import { booksAtom, accessTokenAtom } from '../store'
import { Plus, Pencil, Trash2, X, Check, Loader2, ImagePlus } from 'lucide-react'
import { toast } from 'sonner'
import type { Book } from '../types'
import { createBook, updateBook, deleteBook, fetchBooks } from '../api'

type FormState = {
  id?: string
  title: string; author: string; isbn: string
  description: string; pages: string; year: string; total: string
}

const EMPTY: FormState = { title: '', author: '', isbn: '', description: '', pages: '', year: '', total: '1' }

export function AdminBooksTab() {
  const [books, setBooks] = useAtom(booksAtom)
  const token = useAtomValue(accessTokenAtom)
  const [search, setSearch] = useState('')
  const [form, setForm] = useState<FormState | null>(null)
  const [isNew, setIsNew] = useState(false)
  const [saving, setSaving] = useState(false)
  const [deleting, setDeleting] = useState<string | null>(null)
  const [coverFile, setCoverFile] = useState<File | null>(null)
  const [coverPreview, setCoverPreview] = useState<string | null>(null)
  const fileRef = useRef<HTMLInputElement>(null)

  const filtered = books.filter(
    (b) =>
      b.title.toLowerCase().includes(search.toLowerCase()) ||
      b.author.toLowerCase().includes(search.toLowerCase())
  )

  const set = (key: keyof FormState) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
    setForm((f) => f ? { ...f, [key]: e.target.value } : f)

  const openNew = () => { setIsNew(true); setForm(EMPTY); setCoverFile(null); setCoverPreview(null) }
  const openEdit = (book: Book) => {
    setIsNew(false)
    setCoverFile(null)
    setCoverPreview(book.coverUrl)
    setForm({
      id: book.id, title: book.title, author: book.author, isbn: '',
      description: book.description, pages: String(book.pages || ''),
      year: String(book.year || ''), total: String(book.total),
    })
  }

  const handleCoverChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setCoverFile(file)
    setCoverPreview(URL.createObjectURL(file))
  }

  const handleSave = async () => {
    if (!form || !token) return
    if (!form.title || !form.author) { toast.error('Titre et auteur requis'); return }
    if (isNew && form.isbn.replace(/\D/g, '').length !== 13) { toast.error('ISBN doit contenir 13 chiffres'); return }

    setSaving(true)
    try {
      if (isNew) {
        await createBook({
          titre: form.title, auteur: form.author, isbn: form.isbn,
          description: form.description || undefined,
          nombre_pages: form.pages ? Number(form.pages) : undefined,
          annee_publication: form.year ? Number(form.year) : undefined,
          quantite_totale: form.total ? Number(form.total) : 1,
          couverture: coverFile ?? undefined,
        }, token)
        toast.success('Livre ajouté')
      } else {
        await updateBook(form.id!, {
          titre: form.title, auteur: form.author,
          description: form.description || undefined,
          nombre_pages: form.pages ? Number(form.pages) : undefined,
          annee_publication: form.year ? Number(form.year) : undefined,
          quantite_totale: form.total ? Number(form.total) : undefined,
        }, token)
        toast.success('Livre mis à jour')
      }
      setBooks(await fetchBooks())
      setForm(null)
    } catch (e: any) {
      toast.error(e.message)
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id: string, title: string) => {
    if (!token) return
    setDeleting(id)
    try {
      await deleteBook(id, token)
      setBooks(await fetchBooks())
      toast.success(`"${title}" supprimé`)
    } catch (e: any) {
      toast.error(e.message)
    } finally {
      setDeleting(null)
    }
  }

  return (
    <div className="px-5">
      <div className="flex items-center gap-2 mb-4">
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Rechercher un livre..."
          className="flex-1 px-3 py-2 rounded-xl border border-border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/30"
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

      <p className="text-xs text-gray-400 mb-3">{filtered.length} livre{filtered.length !== 1 ? 's' : ''}</p>

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
                <Pencil className="w-3.5 h-3.5 text-gray-500" />
              </button>
              <button
                onClick={() => handleDelete(book.id, book.title)}
                disabled={deleting === book.id}
                className="w-8 h-8 rounded-lg bg-gray-50 border border-gray-200 flex items-center justify-center hover:bg-red-50 hover:border-red-200 transition-colors disabled:opacity-50"
              >
                {deleting === book.id
                  ? <Loader2 className="w-3.5 h-3.5 animate-spin text-red-400" />
                  : <Trash2 className="w-3.5 h-3.5 text-gray-500" />}
              </button>
            </div>
          </div>
        ))}
      </div>

      {form && (
        <div className="fixed inset-0 z-50 flex flex-col justify-end">
          <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={() => setForm(null)} />
          <div className="relative z-10 bg-card rounded-t-3xl border-t border-border px-6 pt-5 pb-10 shadow-2xl max-w-2xl w-full mx-auto max-h-[85vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-lg font-semibold">{isNew ? 'Ajouter un livre' : 'Modifier'}</h2>
              <button onClick={() => setForm(null)} className="w-8 h-8 rounded-full bg-muted flex items-center justify-center">
                <X className="w-4 h-4 text-muted-foreground" />
              </button>
            </div>

            <div className="space-y-3">
              {([
                { label: 'Titre *', key: 'title' as const },
                { label: 'Auteur *', key: 'author' as const },
                ...(isNew ? [{ label: 'ISBN (13 chiffres) *', key: 'isbn' as const }] : []),
                { label: 'Année', key: 'year' as const },
                { label: 'Pages', key: 'pages' as const },
                { label: 'Exemplaires', key: 'total' as const },
              ]).map(({ label, key }) => (
                <div key={key}>
                  <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">{label}</label>
                  <input
                    value={form[key]}
                    onChange={set(key)}
                    className="mt-1 w-full px-3 py-2.5 rounded-xl border border-border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/30"
                  />
                </div>
              ))}
              <div>
                <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Description</label>
                <textarea
                  value={form.description}
                  onChange={set('description')}
                  rows={2}
                  className="mt-1 w-full px-3 py-2.5 rounded-xl border border-border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 resize-none"
                />
              </div>

              <div>
                <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Couverture</label>
                <input ref={fileRef} type="file" accept="image/*" onChange={handleCoverChange} className="hidden" />
                <button
                  type="button"
                  onClick={() => fileRef.current?.click()}
                  className="mt-1 w-full flex items-center gap-3 px-3 py-2.5 rounded-xl border border-dashed border-border hover:border-primary/50 bg-background transition-colors"
                >
                  {coverPreview ? (
                    <img src={coverPreview} className="w-10 h-14 object-cover rounded-lg flex-shrink-0" />
                  ) : (
                    <div className="w-10 h-14 rounded-lg bg-muted flex items-center justify-center flex-shrink-0">
                      <ImagePlus className="w-4 h-4 text-muted-foreground" />
                    </div>
                  )}
                  <span className="text-sm text-muted-foreground">
                    {coverFile ? coverFile.name : 'Choisir une image…'}
                  </span>
                </button>
              </div>
            </div>

            <button
              onClick={handleSave}
              disabled={saving}
              className="mt-5 w-full flex items-center justify-center gap-2 rounded-full bg-primary py-2.5 text-sm font-medium text-primary-foreground shadow-sm hover:opacity-90 disabled:opacity-50"
            >
              {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4" />}
              {saving ? 'Enregistrement...' : isNew ? 'Ajouter' : 'Enregistrer'}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
