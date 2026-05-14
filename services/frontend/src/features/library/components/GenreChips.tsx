import { useAtom } from 'jotai'
import { genreFilterAtom } from '../store'
import { cn } from '@/lib/utils'

const GENRES = ['Data Engineering', 'Data Science', 'Intelligence Artificielle', 'Informatique', 'Mathématiques', 'Sciences', 'Littérature']

const GENRE_COLORS: Record<string, string> = {
  'Data Engineering': '#0f766e',
  'Data Science': '#0284c7',
  Informatique: '#0369a1',
  'Intelligence Artificielle': '#7c3aed',
  Mathématiques: '#9333ea',
  Sciences: '#059669',
  Littérature: '#b45309',
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
