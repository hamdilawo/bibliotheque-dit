import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  Users, BookMarked, Star,
  LayoutDashboard, LogOut, Menu, X, BookOpen
} from 'lucide-react';
import { useState } from 'react';

const NAV_ITEMS = [
  { to: '/',                label: 'Tableau de bord',  icon: LayoutDashboard },
  { to: '/livres',          label: 'Catalogue',         icon: BookOpen },
  { to: '/emprunts',        label: 'Emprunts',           icon: BookMarked },
  { to: '/utilisateurs',    label: 'Utilisateurs',       icon: Users },
  { to: '/recommandations', label: 'Recommandations',    icon: Star },
];

export default function Navbar() {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);

  const handleLogout = () => { logout(); navigate('/login'); };

  return (
    <nav style={{ backgroundColor: '#1a5f6e' }} className="text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 flex items-center justify-between h-16">
        <Link to="/" className="flex items-center gap-3 font-bold text-lg">
          <img src="/logo-dit.webp" alt="DIT Logo" className="h-9 w-9 rounded object-cover" />
          <div className="flex flex-col leading-tight">
            <span className="text-white font-bold text-base">Bibliothèque</span>
            <span style={{ color: '#7ecfdc' }} className="text-xs font-medium">Dakar Institute of Technology</span>
          </div>
        </Link>

        <div className="hidden md:flex items-center gap-1">
          {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
            <Link
              key={to}
              to={to}
              className="flex items-center gap-1.5 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              style={{
                backgroundColor: location.pathname === to ? '#134d59' : 'transparent',
                color: location.pathname === to ? '#ffffff' : '#b2dde5',
              }}
            >
              <Icon size={16} />
              {label}
            </Link>
          ))}
        </div>

        <div className="hidden md:flex items-center gap-3">
          {user && (
            <div className="text-right">
              <p className="text-sm text-white font-medium">{user.nom_complet}</p>
              <p className="text-xs" style={{ color: '#7ecfdc' }}>{user.type_utilisateur}</p>
            </div>
          )}
          <button
            onClick={handleLogout}
            className="flex items-center gap-1 text-sm transition-colors px-3 py-1.5 rounded-lg"
            style={{ color: '#b2dde5', border: '1px solid #2a7f8e' }}
          >
            <LogOut size={16} /> Déconnexion
          </button>
        </div>

        <button className="md:hidden" onClick={() => setOpen(!open)}>
          {open ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {open && (
        <div style={{ backgroundColor: '#134d59' }} className="md:hidden px-4 pb-4 flex flex-col gap-1">
          {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
            <Link key={to} to={to} onClick={() => setOpen(false)}
              className="flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium text-white">
              <Icon size={16} /> {label}
            </Link>
          ))}
          <button onClick={handleLogout} className="flex items-center gap-2 px-3 py-2 text-sm" style={{ color: '#7ecfdc' }}>
            <LogOut size={16} /> Déconnexion
          </button>
        </div>
      )}
    </nav>
  );
}
