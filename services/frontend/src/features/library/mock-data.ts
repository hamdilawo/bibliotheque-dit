export type Genre =
  | 'Informatique'
  | 'Algorithmique'
  | 'IA & Machine Learning'
  | 'Développement personnel'
  | 'Littérature africaine'
  | 'Classique'
  | 'Sciences'

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

export const BOOKS: Book[] = [
  {
    id: 'b1',
    title: "L'Aventure ambiguë",
    author: 'Cheikh Hamidou Kane',
    genre: 'Littérature africaine',
    description:
      "Roman philosophique majeur de la littérature africaine. Samba Diallo, fils d'un chef peul du Sénégal, est confronté à la rencontre entre l'Islam traditionnel et la civilisation occidentale moderne.",
    coverUrl: 'https://covers.openlibrary.org/b/isbn/9782070365371-L.jpg',
    rating: 4.8,
    borrowCount: 142,
    viewCount: 389,
    available: 2,
    total: 3,
    year: 1961,
    pages: 191,
  },
  {
    id: 'b2',
    title: 'Une si longue lettre',
    author: 'Mariama Bâ',
    genre: 'Littérature africaine',
    description:
      "Un roman épistolaire bouleversant qui explore la condition des femmes dans la société sénégalaise à travers la correspondance entre deux amies d'enfance.",
    coverUrl: 'https://covers.openlibrary.org/b/isbn/9782855890913-L.jpg',
    rating: 4.7,
    borrowCount: 118,
    viewCount: 302,
    available: 1,
    total: 2,
    year: 1979,
    pages: 131,
  },
  {
    id: 'b3',
    title: 'Clean Code',
    author: 'Robert C. Martin',
    genre: 'Informatique',
    description:
      "Un guide pratique pour écrire du code propre, lisible et maintenable. Indispensable pour tout développeur souhaitant améliorer la qualité de son code.",
    coverUrl: 'https://covers.openlibrary.org/b/isbn/9780132350884-L.jpg',
    rating: 4.6,
    borrowCount: 203,
    viewCount: 521,
    available: 2,
    total: 3,
    year: 2008,
    pages: 431,
  },
  {
    id: 'b4',
    title: 'Le Petit Prince',
    author: 'Antoine de Saint-Exupéry',
    genre: 'Classique',
    description:
      "Conte philosophique et poétique sous forme d'un récit pour enfants. Une œuvre intemporelle sur l'amitié, l'amour et le sens de la vie.",
    coverUrl: 'https://covers.openlibrary.org/b/isbn/9782070408504-L.jpg',
    rating: 4.9,
    borrowCount: 287,
    viewCount: 643,
    available: 3,
    total: 5,
    year: 1943,
    pages: 96,
  },
  {
    id: 'b5',
    title: 'Introduction aux Algorithmes',
    author: 'Cormen, Leiserson, Rivest & Stein',
    genre: 'Algorithmique',
    description:
      "La référence incontournable en algorithmique. Couvre les structures de données, les algorithmes de tri, les graphes et bien plus encore.",
    coverUrl: 'https://covers.openlibrary.org/b/isbn/9780262033848-L.jpg',
    rating: 4.5,
    borrowCount: 178,
    viewCount: 445,
    available: 1,
    total: 4,
    year: 2009,
    pages: 1292,
  },
  {
    id: 'b6',
    title: 'Deep Learning',
    author: 'Goodfellow, Bengio & Courville',
    genre: 'IA & Machine Learning',
    description:
      "Le livre de référence sur l'apprentissage profond. Couvre les fondements mathématiques et les architectures modernes de réseaux de neurones.",
    coverUrl: 'https://covers.openlibrary.org/b/isbn/9780262035613-L.jpg',
    rating: 4.4,
    borrowCount: 134,
    viewCount: 378,
    available: 2,
    total: 3,
    year: 2016,
    pages: 775,
  },
  {
    id: 'b7',
    title: 'Atomic Habits',
    author: 'James Clear',
    genre: 'Développement personnel',
    description:
      "Une méthode éprouvée pour prendre de bonnes habitudes et se défaire des mauvaises. Un guide pratique basé sur la science du comportement.",
    coverUrl: 'https://covers.openlibrary.org/b/isbn/9780735211292-L.jpg',
    rating: 4.7,
    borrowCount: 256,
    viewCount: 589,
    available: 2,
    total: 3,
    year: 2018,
    pages: 320,
  },
  {
    id: 'b8',
    title: "L'Étranger",
    author: 'Albert Camus',
    genre: 'Classique',
    description:
      "L'un des romans les plus influents du XXe siècle. L'histoire de Meursault, un homme indifférent au monde qui l'entoure, confronté à la justice humaine.",
    coverUrl: 'https://covers.openlibrary.org/b/isbn/9782070360024-L.jpg',
    rating: 4.5,
    borrowCount: 189,
    viewCount: 412,
    available: 2,
    total: 4,
    year: 1942,
    pages: 184,
  },
  {
    id: 'b9',
    title: 'The Pragmatic Programmer',
    author: 'David Thomas & Andrew Hunt',
    genre: 'Informatique',
    description:
      "Du code au maître artisan. Ce livre couvre tous les aspects du développement logiciel professionnel, de la conception à la livraison.",
    coverUrl: 'https://covers.openlibrary.org/b/isbn/9780201616224-L.jpg',
    rating: 4.6,
    borrowCount: 167,
    viewCount: 398,
    available: 2,
    total: 3,
    year: 2019,
    pages: 352,
  },
  {
    id: 'b10',
    title: '1984',
    author: 'George Orwell',
    genre: 'Classique',
    description:
      "Un roman dystopique visionnaire sur la surveillance de masse, la propagande et le totalitarisme. Plus que jamais d'actualité.",
    coverUrl: 'https://covers.openlibrary.org/b/isbn/9780451524935-L.jpg',
    rating: 4.8,
    borrowCount: 221,
    viewCount: 534,
    available: 1,
    total: 3,
    year: 1949,
    pages: 328,
  },
  {
    id: 'b11',
    title: 'Design Patterns',
    author: 'Gang of Four',
    genre: 'Informatique',
    description:
      "Les patterns de conception orientés objet fondamentaux. Un guide essentiel pour architecturer des logiciels robustes et maintenables.",
    coverUrl: 'https://covers.openlibrary.org/b/isbn/9780201633610-L.jpg',
    rating: 4.3,
    borrowCount: 143,
    viewCount: 356,
    available: 3,
    total: 3,
    year: 1994,
    pages: 395,
  },
  {
    id: 'b12',
    title: 'Penser, vite et lentement',
    author: 'Daniel Kahneman',
    genre: 'Sciences',
    description:
      "Un voyage fascinant dans les deux systèmes qui pilotent notre pensée. Le système 1, rapide et intuitif, et le système 2, lent et délibéré.",
    coverUrl: 'https://covers.openlibrary.org/b/isbn/9780374533557-L.jpg',
    rating: 4.6,
    borrowCount: 198,
    viewCount: 467,
    available: 1,
    total: 2,
    year: 2011,
    pages: 499,
  },
  {
    id: 'b13',
    title: 'Python Crash Course',
    author: 'Eric Matthes',
    genre: 'Informatique',
    description:
      "Introduction rapide et pratique à Python. Parfait pour les débutants qui souhaitent apprendre à programmer avec des projets concrets.",
    coverUrl: 'https://covers.openlibrary.org/b/isbn/9781593279288-L.jpg',
    rating: 4.4,
    borrowCount: 312,
    viewCount: 678,
    available: 2,
    total: 5,
    year: 2019,
    pages: 544,
  },
  {
    id: 'b14',
    title: 'Things Fall Apart',
    author: 'Chinua Achebe',
    genre: 'Littérature africaine',
    description:
      "Le roman le plus célèbre d'Afrique. L'histoire d'Okonkwo et de sa communauté Igbo face au colonialisme britannique au Nigeria.",
    coverUrl: 'https://covers.openlibrary.org/b/isbn/9780385474542-L.jpg',
    rating: 4.7,
    borrowCount: 156,
    viewCount: 345,
    available: 2,
    total: 3,
    year: 1958,
    pages: 209,
  },
  {
    id: 'b15',
    title: 'System Design Interview',
    author: 'Alex Xu',
    genre: 'Informatique',
    description:
      "Guide complet pour réussir les entretiens de conception de systèmes. Couvre les architectures distribuées, la mise à l'échelle et les patterns courants.",
    coverUrl: 'https://covers.openlibrary.org/b/isbn/9781736049112-L.jpg',
    rating: 4.5,
    borrowCount: 189,
    viewCount: 512,
    available: 1,
    total: 2,
    year: 2020,
    pages: 326,
  },
  {
    id: 'b16',
    title: 'Bel-Ami',
    author: 'Guy de Maupassant',
    genre: 'Classique',
    description:
      "L'ascension sociale d'un jeune journaliste sans scrupules dans la société parisienne du XIXe siècle. Un roman sur l'ambition et la corruption.",
    coverUrl: 'https://covers.openlibrary.org/b/isbn/9782070416202-L.jpg',
    rating: 4.3,
    borrowCount: 98,
    viewCount: 267,
    available: 3,
    total: 4,
    year: 1885,
    pages: 369,
  },
  {
    id: 'b17',
    title: 'Mathematics for Machine Learning',
    author: 'Deisenroth, Faisal & Ong',
    genre: 'IA & Machine Learning',
    description:
      "Les fondements mathématiques indispensables pour comprendre et pratiquer le machine learning. Algèbre linéaire, calcul et probabilités.",
    coverUrl: 'https://covers.openlibrary.org/b/isbn/9781108455145-L.jpg',
    rating: 4.4,
    borrowCount: 123,
    viewCount: 334,
    available: 2,
    total: 3,
    year: 2020,
    pages: 417,
  },
  {
    id: 'b18',
    title: 'Les Misérables',
    author: 'Victor Hugo',
    genre: 'Classique',
    description:
      "L'œuvre monumentale de Victor Hugo. L'histoire de Jean Valjean, ancien forçat cherchant à se racheter dans une France du XIXe siècle tourmentée.",
    coverUrl: 'https://covers.openlibrary.org/b/isbn/9782070409228-L.jpg',
    rating: 4.8,
    borrowCount: 167,
    viewCount: 423,
    available: 1,
    total: 2,
    year: 1862,
    pages: 1232,
  },
]

const now = new Date()
const offset = (days: number) => {
  const d = new Date(now)
  d.setDate(d.getDate() + days)
  return d.toISOString()
}

export const LOANS: Loan[] = [
  {
    id: 'l1',
    bookId: 'b3',
    borrowedAt: offset(-10),
    dueAt: offset(4),
    returnedAt: null,
    status: 'active',
  },
  {
    id: 'l2',
    bookId: 'b7',
    borrowedAt: offset(-22),
    dueAt: offset(-8),
    returnedAt: null,
    status: 'overdue',
  },
  {
    id: 'l3',
    bookId: 'b12',
    borrowedAt: offset(-3),
    dueAt: offset(11),
    returnedAt: null,
    status: 'active',
  },
  {
    id: 'l4',
    bookId: 'b4',
    borrowedAt: offset(-45),
    dueAt: offset(-31),
    returnedAt: offset(-33),
    status: 'returned',
  },
  {
    id: 'l5',
    bookId: 'b1',
    borrowedAt: offset(-60),
    dueAt: offset(-46),
    returnedAt: offset(-47),
    status: 'returned',
  },
]

export const CURRENT_USER = {
  name: 'Mamadou Diallo',
  email: 'mdiallo@dit.sn',
  studentId: 'DIT-2024-0847',
  department: 'Génie Logiciel',
}

export const GENRES: Genre[] = [
  'Informatique',
  'Algorithmique',
  'IA & Machine Learning',
  'Littérature africaine',
  'Classique',
  'Sciences',
  'Développement personnel',
]
