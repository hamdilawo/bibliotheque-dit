import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  BookOpen, Users, BookMarked, Star,
  LayoutDashboard, LogOut, Menu, X
} from 'lucide-react';
import { useState } from 'react';

const NAV_ITEMS = [
  { to: '/',              label: 'Tableau de bord', icon: LayoutDashboard },
  { to: '/livres',        label: 'Catalogue',        icon: BookOpen },
  { to: '/emprunts',      label: 'Emprunts',          icon: BookMarked },
  { to: '/utilisateurs',  label: 'Utilisateurs',      icon: Users },
  { to: '/recommandations', label: 'Recommandations', icon: Star },
];

export default function Navbar() {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);

  const handleLogout = () => { logout(); navigate('/login'); };

  return (
    <nav className="bg-blue-900 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 flex items-center justify-between h-16">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2 font-bold text-lg">
          <BookOpen size={24} className="text-blue-300" />
          <span>Bibliothèque <span className="text-blue-300">DIT</span></span>
        </Link>

        {/* Desktop nav */}
        <div className="hidden md:flex items-center gap-1">
          {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
            <Link
              key={to}
              to={to}
              className={`flex items-center gap-1.5 px-3 py-2 rounded-md text-sm font-medium transition-colors
                ${location.pathname === to
                  ? 'bg-blue-700 text-white'
                  : 'text-blue-200 hover:bg-blue-800 hover:text-white'}`}
            >
              <Icon size={16} />
              {label}
            </Link>
          ))}
        </div>

        {/* User + logout */}
        <div className="hidden md:flex items-center gap-3">
          {user && (
            <span className="text-sm text-blue-200">
              {user.nom_complet} <span className="text-xs opacity-60">({user.type_utilisateur})</span>
            </span>
          )}
          <button
            onClick={handleLogout}
            className="flex items-center gap-1 text-sm text-blue-300 hover:text-white transition-colors"
          >
            <LogOut size={16} /> Déconnexion
          </button>
        </div>

        {/* Mobile toggle */}
        <button className="md:hidden" onClick={() => setOpen(!open)}>
          {open ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Mobile menu */}
      {open && (
        <div className="md:hidden bg-blue-800 px-4 pb-4 flex flex-col gap-1">
          {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
            <Link
              key={to}
              to={to}
              onClick={() => setOpen(false)}
              className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium
                ${location.pathname === to ? 'bg-blue-700' : 'hover:bg-blue-700'}`}
            >
              <Icon size={16} /> {label}
            </Link>
          ))}
          <button onClick={handleLogout} className="flex items-center gap-2 px-3 py-2 text-sm text-blue-300">
            <LogOut size={16} /> Déconnexion
          </button>
        </div>
      )}
    </nav>
  );
}
