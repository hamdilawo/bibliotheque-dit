import { useState, useEffect } from 'react';
import { Star, RefreshCw, Zap, BarChart2 } from 'lucide-react';
import { recoService } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { Card, Button, Spinner, EmptyState, StatCard } from '../components/UI';
import toast from 'react-hot-toast';

function RecoCard({ reco, rank }) {
  return (
    <Card className="flex items-start gap-4 hover:shadow-md transition-shadow">
      <div className="w-10 h-10 rounded-full bg-yellow-100 text-yellow-700 flex items-center
        justify-center font-bold text-lg shrink-0">
        {rank}
      </div>
      <div className="flex-1 min-w-0">
        <h3 className="font-semibold text-gray-800 truncate">
          {reco.titre || `Livre #${reco.livre_id}`}
        </h3>
        {reco.auteur && <p className="text-sm text-gray-500">{reco.auteur}</p>}
        {reco.isbn && <p className="text-xs text-gray-400 mt-0.5">ISBN : {reco.isbn}</p>}
      </div>
      <div className="text-right shrink-0">
        <span className={`text-xs px-2 py-1 rounded-full font-medium ${
          reco.disponible ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'
        }`}>
          {reco.disponible === undefined ? '—' : reco.disponible ? 'Disponible' : 'Indisponible'}
        </span>
        <div className="flex items-center gap-1 justify-end mt-1">
          <Star size={11} className="text-yellow-400 fill-yellow-400" />
          <span className="text-xs text-gray-400">{reco.score}</span>
        </div>
      </div>
    </Card>
  );
}

export default function RecommandationsPage() {
  const { user } = useAuth();
  const [recos, setRecos] = useState([]);
  const [populaires, setPopulaires] = useState([]);
  const [metriques, setMetriques] = useState(null);
  const [loading, setLoading] = useState(true);
  const [entrainement, setEntrainement] = useState(false);
  const [message, setMessage] = useState('');

  const charger = async () => {
    setLoading(true);
    try {
      const [recosRes, popRes, metRes] = await Promise.all([
        user ? recoService.recommandations(user.id, 8) : Promise.resolve(null),
        recoService.populaires(6),
        recoService.metriques(),
      ]);
      if (recosRes) {
        setRecos(recosRes.data.recommandations || []);
        setMessage(recosRes.data.message || '');
      }
      setPopulaires(popRes.data.top_livres || []);
      setMetriques(metRes.data);
    } catch (err) {
      if (err.response?.status === 503) {
        toast.error('Modèle non disponible. Lancez un entraînement.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { charger(); }, [user]);

  const handleEntrainer = async () => {
    setEntrainement(true);
    try {
      await recoService.entrainer();
      toast.success('Entraînement lancé ! Actualisez dans quelques secondes.');
      setTimeout(charger, 3000);
    } catch {
      toast.error('Erreur lors du lancement de l\'entraînement.');
    } finally {
      setEntrainement(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Entête */}
      <div className="flex items-center justify-between mb-6 flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
            <Star className="text-yellow-500" /> Recommandations
          </h1>
          <p className="text-sm text-gray-500 mt-0.5">
            Basées sur votre historique d'emprunts (SVD)
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={charger}>
            <RefreshCw size={14} /> Actualiser
          </Button>
          <Button onClick={handleEntrainer} disabled={entrainement}>
            <Zap size={14} />
            {entrainement ? 'Entraînement...' : 'Ré-entraîner le modèle'}
          </Button>
        </div>
      </div>

      {/* Métriques du modèle */}
      {metriques && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-8">
          {[
            { label: 'Utilisateurs', val: metriques.n_utilisateurs, color: 'text-blue-600 bg-blue-50' },
            { label: 'Livres indexés', val: metriques.n_livres, color: 'text-purple-600 bg-purple-50' },
            { label: 'Emprunts analysés', val: metriques.n_emprunts, color: 'text-green-600 bg-green-50' },
            { label: 'Variance SVD', val: `${(metriques.variance_expliquee * 100).toFixed(1)}%`, color: 'text-amber-600 bg-amber-50' },
          ].map(s => (
            <div key={s.label} className={`rounded-xl p-4 ${s.color}`}>
              <p className="text-xl font-bold">{s.val}</p>
              <p className="text-xs mt-0.5 opacity-80">{s.label}</p>
            </div>
          ))}
        </div>
      )}

      {loading ? (
        <div className="flex justify-center py-16"><Spinner size="lg" /></div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Recommandations personnalisées */}
          <div className="lg:col-span-2">
            <h2 className="font-semibold text-gray-700 mb-3 flex items-center gap-2">
              <Star size={16} className="text-yellow-500" />
              Personnalisées pour vous
              {message && <span className="text-xs text-gray-400 font-normal">· {message}</span>}
            </h2>
            {recos.length === 0 ? (
              <EmptyState
                icon={Star}
                title="Pas encore de recommandations"
                description="Empruntez quelques livres, puis lancez un ré-entraînement du modèle."
              />
            ) : (
              <div className="flex flex-col gap-3">
                {recos.map((r, i) => <RecoCard key={r.livre_id} reco={r} rank={i + 1} />)}
              </div>
            )}
          </div>

          {/* Populaires */}
          <div>
            <h2 className="font-semibold text-gray-700 mb-3 flex items-center gap-2">
              <BarChart2 size={16} className="text-blue-500" />
              Les plus empruntés
            </h2>
            <Card className="p-0 overflow-hidden">
              {populaires.length === 0 ? (
                <p className="text-sm text-gray-400 p-4">Aucune donnée.</p>
              ) : (
                <div>
                  {populaires.map((l, i) => (
                    <div key={l.livre_id}
                      className="flex items-center gap-3 px-4 py-3 border-b last:border-0">
                      <span className="text-sm font-bold text-gray-400 w-5">{i + 1}</span>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-800">Livre #{l.livre_id}</p>
                        <div className="w-full bg-gray-100 rounded-full h-1.5 mt-1">
                          <div
                            className="bg-blue-500 h-1.5 rounded-full"
                            style={{ width: `${Math.min(100, (l.emprunts / populaires[0].emprunts) * 100)}%` }}
                          />
                        </div>
                      </div>
                      <span className="text-xs text-gray-500 shrink-0">{l.emprunts} emprunts</span>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          </div>
        </div>
      )}
    </div>
  );
}
