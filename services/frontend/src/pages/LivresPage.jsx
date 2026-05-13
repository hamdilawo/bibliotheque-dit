import { useState, useEffect, useCallback } from 'react';
import { Search, Plus, BookOpen, Filter } from 'lucide-react';
import { livresService, empruntsService } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { Card, Badge, Button, Spinner, EmptyState } from '../components/UI';
import toast from 'react-hot-toast';

function LivreCard({ livre, onEmprunter }) {
  return (
    <Card className="flex flex-col justify-between hover:shadow-md transition-shadow">
      <div>
        <div className="flex items-start justify-between gap-2 mb-2">
          <h3 className="font-semibold text-gray-800 text-sm leading-snug line-clamp-2">
            {livre.titre}
          </h3>
          <Badge label={livre.disponible ? 'ACTIF' : 'INACTIF'} />
        </div>
        <p className="text-xs text-gray-500 mb-1">✍ {livre.auteur}</p>
        {livre.categorie_nom && (
          <p className="text-xs text-blue-600 mb-2">{livre.categorie_nom}</p>
        )}
        <p className="text-xs text-gray-400">ISBN : {livre.isbn}</p>
      </div>
      <div className="mt-4 flex items-center justify-between">
        <span className="text-xs text-gray-500">
          {livre.quantite_disponible}/{livre.quantite_totale} dispo
        </span>
        <Button
          size="sm"
          disabled={!livre.disponible}
          onClick={() => onEmprunter(livre)}
        >
          Emprunter
        </Button>
      </div>
    </Card>
  );
}

function AjouterLivreModal({ onClose, onSuccess }) {
  const [form, setForm] = useState({
    titre: '', auteur: '', isbn: '', editeur: '',
    annee_publication: '', langue: 'fr', quantite_totale: 1,
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await livresService.creer({
        ...form,
        quantite_disponible: form.quantite_totale,
        annee_publication: form.annee_publication || null,
      });
      toast.success('Livre ajouté !');
      onSuccess();
    } catch (err) {
      toast.error(err.response?.data?.isbn?.[0] || 'Erreur lors de l\'ajout.');
    } finally {
      setLoading(false);
    }
  };

  const field = (name, label, type = 'text', extra = {}) => (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      <input
        type={type}
        value={form[name]}
        onChange={e => setForm({ ...form, [name]: e.target.value })}
        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm
          focus:outline-none focus:ring-2 focus:ring-blue-500"
        {...extra}
      />
    </div>
  );

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <h2 className="text-lg font-bold text-gray-800 mb-4">Ajouter un livre</h2>
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            {field('titre', 'Titre *', 'text', { required: true })}
            {field('auteur', 'Auteur *', 'text', { required: true })}
            {field('isbn', 'ISBN *', 'text', { required: true, placeholder: '9782100780730' })}
            {field('editeur', 'Éditeur')}
            <div className="grid grid-cols-2 gap-3">
              {field('annee_publication', 'Année', 'number')}
              {field('quantite_totale', 'Quantité', 'number', { min: 1 })}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Langue</label>
              <select
                value={form.langue}
                onChange={e => setForm({ ...form, langue: e.target.value })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="fr">Français</option>
                <option value="en">Anglais</option>
                <option value="ar">Arabe</option>
                <option value="es">Espagnol</option>
              </select>
            </div>
            <div className="flex gap-3 pt-2">
              <Button type="button" variant="outline" className="flex-1" onClick={onClose}>Annuler</Button>
              <Button type="submit" className="flex-1" disabled={loading}>
                {loading ? 'Ajout...' : 'Ajouter'}
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default function LivresPage() {
  const { user } = useAuth();
  const [livres, setLivres] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filtreDisponible, setFiltreDisponible] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);

  const charger = useCallback(async () => {
    setLoading(true);
    try {
      const params = { page };
      if (search) params.q = search;
      if (filtreDisponible) params.disponible = true;
      const fn = search ? livresService.rechercher : livresService.lister;
      const res = await fn(params);
      setLivres(res.data.results || []);
      setTotal(res.data.count || 0);
    } catch {
      toast.error('Erreur de chargement du catalogue.');
    } finally {
      setLoading(false);
    }
  }, [search, filtreDisponible, page]);

  useEffect(() => { charger(); }, [charger]);

  const handleEmprunter = async (livre) => {
    if (!user) return toast.error('Connectez-vous d\'abord.');
    try {
      await empruntsService.emprunter({ utilisateur_id: user.id, livre_id: livre.id });
      toast.success(`"${livre.titre}" emprunté avec succès !`);
      charger();
    } catch (err) {
      toast.error(err.response?.data?.error || 'Erreur lors de l\'emprunt.');
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Entête */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Catalogue</h1>
          <p className="text-sm text-gray-500 mt-0.5">{total} livre(s) trouvé(s)</p>
        </div>
        <Button onClick={() => setShowModal(true)}>
          <Plus size={16} /> Ajouter
        </Button>
      </div>

      {/* Filtres */}
      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Rechercher par titre, auteur, ISBN..."
            value={search}
            onChange={e => { setSearch(e.target.value); setPage(1); }}
            className="w-full pl-9 pr-4 py-2 border border-gray-300 rounded-lg text-sm
              focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <button
          onClick={() => setFiltreDisponible(!filtreDisponible)}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg border text-sm font-medium transition-colors
            ${filtreDisponible ? 'bg-blue-600 text-white border-blue-600' : 'border-gray-300 text-gray-600 hover:bg-gray-50'}`}
        >
          <Filter size={14} /> Disponibles uniquement
        </button>
      </div>

      {/* Grille */}
      {loading ? (
        <div className="flex justify-center py-16"><Spinner size="lg" /></div>
      ) : livres.length === 0 ? (
        <EmptyState icon={BookOpen} title="Aucun livre trouvé" description="Essayez un autre terme de recherche." />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {livres.map(livre => (
            <LivreCard key={livre.id} livre={livre} onEmprunter={handleEmprunter} />
          ))}
        </div>
      )}

      {/* Pagination */}
      {total > 20 && (
        <div className="flex justify-center gap-2 mt-8">
          <Button variant="outline" size="sm" disabled={page === 1} onClick={() => setPage(p => p - 1)}>
            ← Précédent
          </Button>
          <span className="px-4 py-1.5 text-sm text-gray-600">Page {page}</span>
          <Button variant="outline" size="sm" disabled={livres.length < 20} onClick={() => setPage(p => p + 1)}>
            Suivant →
          </Button>
        </div>
      )}

      {/* Modal ajout */}
      {showModal && (
        <AjouterLivreModal
          onClose={() => setShowModal(false)}
          onSuccess={() => { setShowModal(false); charger(); }}
        />
      )}
    </div>
  );
}
