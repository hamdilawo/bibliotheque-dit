import { useState, useEffect, useCallback } from 'react';
import { BookMarked, AlertTriangle, Download, RotateCcw } from 'lucide-react';
import { empruntsService } from '../services/api';
import { Card, Badge, Button, Spinner, EmptyState } from '../components/UI';
import toast from 'react-hot-toast';

export default function EmpruntsPage() {
  const [emprunts, setEmprunts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filtre, setFiltre] = useState('tous');
  const [stats, setStats] = useState(null);

  const charger = useCallback(async () => {
    setLoading(true);
    try {
      const [empRes, statsRes] = await Promise.all([
        filtre === 'retards'
          ? empruntsService.retards()
          : empruntsService.lister(filtre !== 'tous' ? { statut: filtre } : {}),
        empruntsService.statistiques(),
      ]);
      setEmprunts(empRes.data.results || empRes.data || []);
      setStats(statsRes.data);
    } catch {
      toast.error('Erreur de chargement.');
    } finally {
      setLoading(false);
    }
  }, [filtre]);

  useEffect(() => { charger(); }, [charger]);

  const handleRetour = async (emprunt) => {
    try {
      const res = await empruntsService.retourner(emprunt.id, {});
      toast.success(res.data.message || 'Retour enregistré !');
      charger();
    } catch (err) {
      toast.error(err.response?.data?.error || 'Erreur lors du retour.');
    }
  };

  const handleExportCsv = async () => {
    try {
      const res = await empruntsService.exportCsv();
      const url = URL.createObjectURL(new Blob([res.data]));
      const a = document.createElement('a');
      a.href = url; a.download = 'loans.csv'; a.click();
      URL.revokeObjectURL(url);
      toast.success('Export CSV téléchargé !');
    } catch {
      toast.error('Erreur lors de l\'export.');
    }
  };

  const FILTRES = [
    { key: 'tous', label: 'Tous' },
    { key: 'EN_COURS', label: 'En cours' },
    { key: 'retards', label: '⚠ Retards' },
    { key: 'RETOURNE', label: 'Retournés' },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Entête */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Emprunts</h1>
          <p className="text-sm text-gray-500 mt-0.5">
            {stats ? `${stats.en_cours} en cours · ${stats.en_retard} en retard` : ''}
          </p>
        </div>
        <Button variant="outline" onClick={handleExportCsv}>
          <Download size={16} /> Export CSV
        </Button>
      </div>

      {/* Stats rapides */}
      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
          {[
            { label: 'En cours', val: stats.en_cours, color: 'text-blue-600 bg-blue-50' },
            { label: 'En retard', val: stats.en_retard, color: 'text-red-600 bg-red-50' },
            { label: 'Retournés', val: stats.retournes, color: 'text-green-600 bg-green-50' },
            { label: 'Pénalités', val: `${stats.penalites_totales_fcfa} F`, color: 'text-orange-600 bg-orange-50' },
          ].map(s => (
            <div key={s.label} className={`rounded-xl p-4 ${s.color}`}>
              <p className="text-xl font-bold">{s.val}</p>
              <p className="text-xs mt-0.5 opacity-80">{s.label}</p>
            </div>
          ))}
        </div>
      )}

      {/* Filtres */}
      <div className="flex gap-2 mb-6 flex-wrap">
        {FILTRES.map(f => (
          <button
            key={f.key}
            onClick={() => setFiltre(f.key)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors
              ${filtre === f.key
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* Liste */}
      {loading ? (
        <div className="flex justify-center py-16"><Spinner size="lg" /></div>
      ) : emprunts.length === 0 ? (
        <EmptyState icon={BookMarked} title="Aucun emprunt" description="Aucun emprunt pour ce filtre." />
      ) : (
        <div className="flex flex-col gap-3">
          {emprunts.map(e => (
            <Card key={e.id} className="flex items-center gap-4 py-4">
              <div className={`p-2 rounded-lg shrink-0 ${
                e.statut === 'EN_RETARD' ? 'bg-red-100' :
                e.statut === 'RETOURNE'  ? 'bg-green-100' : 'bg-blue-100'
              }`}>
                {e.statut === 'EN_RETARD'
                  ? <AlertTriangle size={20} className="text-red-600" />
                  : <BookMarked size={20} className="text-blue-600" />}
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-gray-800 truncate">{e.livre_titre}</p>
                <p className="text-xs text-gray-500">{e.utilisateur_nom} · {e.utilisateur_carte}</p>
                <p className="text-xs text-gray-400 mt-0.5">
                  Emprunté le {new Date(e.date_emprunt).toLocaleDateString('fr-FR')} ·
                  Retour prévu : {new Date(e.date_retour_prevue).toLocaleDateString('fr-FR')}
                </p>
              </div>
              <div className="text-right shrink-0">
                <Badge label={e.statut} />
                {e.jours_retard > 0 && (
                  <p className="text-xs text-red-500 mt-1">{e.jours_retard}j · {e.penalite_fcfa} FCFA</p>
                )}
                {e.statut !== 'RETOURNE' && (
                  <Button
                    size="sm"
                    variant="outline"
                    className="mt-2"
                    onClick={() => handleRetour(e)}
                  >
                    <RotateCcw size={13} /> Retour
                  </Button>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
