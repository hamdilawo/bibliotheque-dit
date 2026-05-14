import { useAtom } from 'jotai'
import { searchAtom } from '../store'
import { Search, X } from 'lucide-react'

export function SearchBar() {
  const [search, setSearch] = useAtom(searchAtom)

  return (
    <div className="relative mx-5">
      <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
      <input
        type="text"
        placeholder="Rechercher un livre ou un auteur…"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="w-full pl-11 pr-10 py-3.5 rounded-2xl bg-white border border-gray-200 text-sm outline-none focus:border-[#004455] focus:ring-2 focus:ring-[#004455]/15 transition-all placeholder:text-gray-400 shadow-sm"
      />
      {search && (
        <button
          onClick={() => setSearch('')}
          className="absolute right-3 top-1/2 -translate-y-1/2 w-6 h-6 rounded-full bg-gray-100 flex items-center justify-center"
        >
          <X className="w-3 h-3 text-gray-500" />
        </button>
      )}
    </div>
  )
}
