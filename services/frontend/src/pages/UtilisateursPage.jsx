import { useState, useEffect, useCallback } from 'react';
import { Search, UserPlus, Users } from 'lucide-react';
import { usersService } from '../services/api';
import { Card, Badge, Button, Spinner, EmptyState } from '../components/UI';
import toast from 'react-hot-toast';

function UserCard({ user }) {
  return (
    <Card className="hover:shadow-md transition-shadow">
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-full bg-blue-100 text-blue-700 flex items-center
          justify-center font-bold text-sm shrink-0">
          {user.nom_complet?.charAt(0) || '?'}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <p className="font-semibold text-gray-800 text-sm">{user.nom_complet}</p>
            <Badge label={user.type_utilisateur} />
            <Badge label={user.statut} />
          </div>
          <p className="text-xs text-gray-500 mt-0.5">{user.email}</p>
          <p className="text-xs text-gray-400">Carte : {user.numero_carte}</p>
        </div>
        <div className="text-right shrink-0">
          <p className="text-sm font-bold text-gray-700">
            {user.emprunts_en_cours}/{user.quota_emprunts}
          </p>
          <p className="text-xs text-gray-400">emprunts</p>
        </div>
      </div>
    </Card>
  );
}

function AjouterUserModal({ onClose, onSuccess }) {
  const [form, setForm] = useState({
    email: '', nom: '', prenom: '', numero_carte: '',
    type_utilisateur: 'ETUDIANT', telephone: '', password: '',
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await usersService.creer(form);
      toast.success('Utilisateur créé !');
      onSuccess();
    } catch (err) {
      const errors = err.response?.data;
      const msg = errors?.email?.[0] || errors?.numero_carte?.[0] || 'Erreur lors de la création.';
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  const field = (name, label, type = 'text', required = false) => (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      <input type={type} required={required} value={form[name]}
        onChange={e => setForm({ ...form, [name]: e.target.value })}
        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm
          focus:outline-none focus:ring-2 focus:ring-blue-500" />
    </div>
  );

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-md max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <h2 className="text-lg font-bold text-gray-800 mb-4">Nouvel utilisateur</h2>
          <form onSubmit={handleSubmit} className="flex flex-col gap-3">
            <div className="grid grid-cols-2 gap-3">
              {field('prenom', 'Prénom *', 'text', true)}
              {field('nom', 'Nom *', 'text', true)}
            </div>
            {field('email', 'Email *', 'email', true)}
            {field('numero_carte', 'N° Carte *', 'text', true)}
            {field('telephone', 'Téléphone')}
            {field('password', 'Mot de passe *', 'password', true)}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
              <select value={form.type_utilisateur}
                onChange={e => setForm({ ...form, type_utilisateur: e.target.value })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="ETUDIANT">Étudiant</option>
                <option value="PROFESSEUR">Professeur</option>
                <option value="PERSONNEL">Personnel</option>
                <option value="ADMIN">Admin</option>
              </select>
            </div>
            <div className="flex gap-3 pt-2">
              <Button type="button" variant="outline" className="flex-1" onClick={onClose}>Annuler</Button>
              <Button type="submit" className="flex-1" disabled={loading}>
                {loading ? 'Création...' : 'Créer'}
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default function UtilisateursPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [typeFiltre, setTypeFiltre] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [stats, setStats] = useState(null);

  const charger = useCallback(async () => {
    setLoading(true);
    try {
      const params = {};
      if (search) params.q = search;
      if (typeFiltre) params.type = typeFiltre;
      const [usersRes, statsRes] = await Promise.all([
        search || typeFiltre ? usersService.rechercher(params) : usersService.lister(),
        usersService.statistiques(),
      ]);
      setUsers(usersRes.data.results || []);
      setStats(statsRes.data);
    } catch { toast.error('Erreur de chargement.'); }
    finally { setLoading(false); }
  }, [search, typeFiltre]);

  useEffect(() => { charger(); }, [charger]);

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Utilisateurs</h1>
          {stats && (
            <p className="text-sm text-gray-500 mt-0.5">
              {stats.total} au total · {stats.actifs} actifs ·
              {stats.par_type.etudiants} étudiants · {stats.par_type.professeurs} professeurs
            </p>
          )}
        </div>
        <Button onClick={() => setShowModal(true)}>
          <UserPlus size={16} /> Nouveau
        </Button>
      </div>

      {/* Filtres */}
      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input type="text" placeholder="Nom, email, numéro de carte..."
            value={search} onChange={e => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 border border-gray-300 rounded-lg text-sm
              focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <select value={typeFiltre} onChange={e => setTypeFiltre(e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
          <option value="">Tous les types</option>
          <option value="ETUDIANT">Étudiants</option>
          <option value="PROFESSEUR">Professeurs</option>
          <option value="PERSONNEL">Personnel</option>
          <option value="ADMIN">Admins</option>
        </select>
      </div>

      {loading ? (
        <div className="flex justify-center py-16"><Spinner size="lg" /></div>
      ) : users.length === 0 ? (
        <EmptyState icon={Users} title="Aucun utilisateur" description="Essayez un autre filtre." />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {users.map(u => <UserCard key={u.id} user={u} />)}
        </div>
      )}

      {showModal && (
        <AjouterUserModal
          onClose={() => setShowModal(false)}
          onSuccess={() => { setShowModal(false); charger(); }}
        />
      )}
    </div>
  );
}
