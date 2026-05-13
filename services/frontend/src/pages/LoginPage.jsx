import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(form.email, form.password);
      toast.success('Connexion réussie !');
      navigate('/');
    } catch {
      toast.error('Email ou mot de passe incorrect.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4"
      style={{ background: 'linear-gradient(135deg, #1a5f6e 0%, #0d3940 100%)' }}>
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8">

        {/* Logo DIT */}
        <div className="flex flex-col items-center mb-8">
          <img
            src="/logo-dit.webp"
            alt="DIT Logo"
            className="h-20 w-20 rounded-xl object-cover mb-4 shadow-md"
          />
          <h1 className="text-2xl font-bold" style={{ color: '#1a5f6e' }}>
            Bibliothèque DIT
          </h1>
          <p className="text-sm text-gray-500 mt-1">Master 2 Intelligence Artificielle</p>
          <p className="text-xs text-gray-400 mt-0.5">Dakar Institute of Technology</p>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              type="email"
              required
              placeholder="votre.email@dit.sn"
              value={form.email}
              onChange={e => setForm({ ...form, email: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm
                focus:outline-none focus:ring-2"
              style={{ '--tw-ring-color': '#1a5f6e' }}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Mot de passe</label>
            <input
              type="password"
              required
              placeholder="••••••••"
              value={form.password}
              onChange={e => setForm({ ...form, password: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm
                focus:outline-none focus:ring-2"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="text-white font-medium py-2.5 rounded-lg transition-colors disabled:opacity-60 mt-2"
            style={{ backgroundColor: loading ? '#134d59' : '#1a5f6e' }}
          >
            {loading ? 'Connexion...' : 'Se connecter'}
          </button>
        </form>

        <div className="mt-6 p-4 rounded-lg text-xs text-gray-500" style={{ backgroundColor: '#f0fafb' }}>
          <p className="font-medium mb-1" style={{ color: '#1a5f6e' }}>Comptes de démonstration :</p>
          <p>admin@dit.sn / DIT@Admin2026!</p>
          <p>moussa.ba@etu.dit.sn / Etu@2026!</p>
        </div>
      </div>
    </div>
  );
}
