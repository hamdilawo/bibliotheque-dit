import { createFileRoute } from '@tanstack/react-router'
import { LibraryShell } from '@/features/library/components/LibraryShell'

export const Route = createFileRoute('/$lang/')({
  component: LibraryHome,
  head: () => ({
    meta: [
      { title: 'DIT Library — Bibliothèque numérique' },
      { name: 'description', content: 'Découvrez, empruntez et gérez vos livres à la bibliothèque DIT.' },
    ],
  }),
})

function LibraryHome() {
  return <LibraryShell />
}
