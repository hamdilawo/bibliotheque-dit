import { useAtom } from 'jotai'
import { genreFilterAtom } from '../store'
import { GENRES } from '../mock-data'
import { cn } from '@/lib/utils'

const GENRE_COLORS: Record<string, string> = {
  Informatique: '#0369a1',
  Algorithmique: '#7c3aed',
  'IA & Machine Learning': '#0d9488',
  'Littérature africaine': '#b45309',
  Classique: '#be185d',
  Sciences: '#059669',
  'Développement personnel': '#4338ca',
}

export function GenreChips() {
  const [genre, setGenre] = useAtom(genreFilterAtom)

  return (
    <div
      className="flex gap-2 overflow-x-auto px-5 pb-1"
      style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' } as React.CSSProperties}
    >
      <button
        onClick={() => setGenre(null)}
        className={cn(
          'flex-shrink-0 px-4 py-1.5 rounded-full text-xs font-semibold transition-all border',
          !genre ? 'text-white border-transparent shadow-sm' : 'bg-white text-gray-600 border-gray-200'
        )}
        style={!genre ? { backgroundColor: '#004455' } : undefined}
      >
        Tout
      </button>
      {GENRES.map((g) => (
        <button
          key={g}
          onClick={() => setGenre(genre === g ? null : g)}
          className={cn(
            'flex-shrink-0 px-4 py-1.5 rounded-full text-xs font-semibold transition-all border whitespace-nowrap',
            genre === g ? 'text-white border-transparent shadow-sm' : 'bg-white text-gray-600 border-gray-200'
          )}
          style={genre === g ? { backgroundColor: GENRE_COLORS[g] ?? '#004455' } : undefined}
        >
          {g}
        </button>
      ))}
    </div>
  )
}
