// Carte générique
export function Card({ children, className = '' }) {
  return (
    <div className={`bg-white rounded-xl shadow-sm border border-gray-100 p-6 ${className}`}>
      {children}
    </div>
  );
}

// Badge de statut
const BADGE_COLORS = {
  EN_COURS:  'bg-blue-100 text-blue-800',
  RETOURNE:  'bg-green-100 text-green-800',
  EN_RETARD: 'bg-red-100 text-red-800',
  PERDU:     'bg-gray-100 text-gray-800',
  ACTIF:     'bg-green-100 text-green-800',
  SUSPENDU:  'bg-orange-100 text-orange-800',
  INACTIF:   'bg-gray-100 text-gray-800',
  ETUDIANT:  'bg-indigo-100 text-indigo-800',
  PROFESSEUR:'bg-purple-100 text-purple-800',
  PERSONNEL: 'bg-teal-100 text-teal-800',
  ADMIN:     'bg-red-100 text-red-800',
};

export function Badge({ label }) {
  const color = BADGE_COLORS[label] || 'bg-gray-100 text-gray-700';
  return (
    <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${color}`}>
      {label}
    </span>
  );
}

// Bouton
export function Button({ children, variant = 'primary', size = 'md', className = '', ...props }) {
  const base = 'inline-flex items-center gap-2 font-medium rounded-lg transition-colors disabled:opacity-50';
  const sizes = { sm: 'px-3 py-1.5 text-sm', md: 'px-4 py-2 text-sm', lg: 'px-6 py-3 text-base' };
  const variants = {
    primary:  'bg-blue-600 text-white hover:bg-blue-700',
    secondary:'bg-gray-100 text-gray-700 hover:bg-gray-200',
    danger:   'bg-red-600 text-white hover:bg-red-700',
    success:  'bg-green-600 text-white hover:bg-green-700',
    outline:  'border border-gray-300 text-gray-700 hover:bg-gray-50',
  };
  return (
    <button className={`${base} ${sizes[size]} ${variants[variant]} ${className}`} {...props}>
      {children}
    </button>
  );
}

// Champ de saisie
export function Input({ label, error, className = '', ...props }) {
  return (
    <div className="flex flex-col gap-1">
      {label && <label className="text-sm font-medium text-gray-700">{label}</label>}
      <input
        className={`border border-gray-300 rounded-lg px-3 py-2 text-sm
          focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
          ${error ? 'border-red-400' : ''} ${className}`}
        {...props}
      />
      {error && <p className="text-xs text-red-500">{error}</p>}
    </div>
  );
}

// Loader spinner
export function Spinner({ size = 'md' }) {
  const s = { sm: 'w-4 h-4', md: 'w-8 h-8', lg: 'w-12 h-12' }[size];
  return (
    <div className={`${s} border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin`} />
  );
}

// État vide
export function EmptyState({ icon: Icon, title, description }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center text-gray-400">
      <Icon size={48} className="mb-4 opacity-40" />
      <p className="font-medium text-gray-600">{title}</p>
      {description && <p className="text-sm mt-1">{description}</p>}
    </div>
  );
}

// Stat card pour le dashboard
export function StatCard({ label, value, icon: Icon, color = 'blue', sub }) {
  const colors = {
    blue:   'bg-blue-50 text-blue-600',
    green:  'bg-green-50 text-green-600',
    red:    'bg-red-50 text-red-600',
    purple: 'bg-purple-50 text-purple-600',
    amber:  'bg-amber-50 text-amber-600',
  };
  return (
    <Card>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500">{label}</p>
          <p className="text-3xl font-bold text-gray-800 mt-1">{value}</p>
          {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
        </div>
        <div className={`p-3 rounded-xl ${colors[color]}`}>
          <Icon size={24} />
        </div>
      </div>
    </Card>
  );
}
