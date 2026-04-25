import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { BookOpen, Users, BookMarked, AlertTriangle, Star, TrendingUp } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { empruntsService, livresService, usersService, recoService } from '../services/api';
import { StatCard, Card, Spinner, Badge } from '../components/UI';

export default function DashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [retards, setRetards] = useState([]);
  const [recos, setRecos] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      empruntsService.statistiques(),
      usersService.statistiques(),
      empruntsService.retards(),
      user ? recoService.recommandations(user.id, 4) : Promise.resolve(null),
    ]).then(([empStats, usrStats, retardsRes, recosRes]) => {
      setStats({
        emprunts: empStats.data,
        utilisateurs: usrStats.data,
      });
      setRetards(retardsRes.data.results?.slice(0, 5) || []);
      if (recosRes) setRecos(recosRes.data.recommandations || []);
    }).catch(() => {}).finally(() => setLoading(false));
  }, [user]);

  if (loading) return (
    <div className="flex justify-center items-center h-64">
      <Spinner size="lg" />
    </div>
  );

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Bienvenue */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-800">
          Bonjour, {user?.nom_complet || 'Utilisateur'} 👋
        </h1>
        <p className="text-gray-500 mt-1">Voici un aperçu de la bibliothèque DIT</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard
          label="Emprunts en cours"
          value={stats?.emprunts?.en_cours ?? '—'}
          icon={BookMarked}
          color="blue"
        />
        <StatCard
          label="En retard"
          value={stats?.emprunts?.en_retard ?? '—'}
          icon={AlertTriangle}
          color="red"
          sub={stats?.emprunts?.penalites_totales_fcfa
            ? `${stats.emprunts.penalites_totales_fcfa} FCFA de pénalités`
            : undefined}
        />
        <StatCard
          label="Utilisateurs actifs"
          value={stats?.utilisateurs?.actifs ?? '—'}
          icon={Users}
          color="green"
        />
        <StatCard
          label="Emprunts total"
          value={stats?.emprunts?.total_emprunts ?? '—'}
          icon={TrendingUp}
          color="purple"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Retards */}
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-gray-800 flex items-center gap-2">
              <AlertTriangle size={18} className="text-red-500" />
              Retards récents
            </h2>
            <Link to="/emprunts?statut=EN_RETARD" className="text-sm text-blue-600 hover:underline">
              Voir tout
            </Link>
          </div>
          {retards.length === 0 ? (
            <p className="text-sm text-gray-400 text-center py-8">Aucun retard 🎉</p>
          ) : (
            <div className="flex flex-col gap-3">
              {retards.map(e => (
                <div key={e.id} className="flex items-center justify-between py-2 border-b last:border-0">
                  <div>
                    <p className="text-sm font-medium text-gray-800 truncate max-w-[180px]">{e.livre_titre}</p>
                    <p className="text-xs text-gray-500">{e.utilisateur_nom}</p>
                  </div>
                  <div className="text-right">
                    <Badge label="EN_RETARD" />
                    <p className="text-xs text-red-500 mt-1">{e.jours_retard}j — {e.penalite_fcfa} FCFA</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>

        {/* Recommandations */}
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-gray-800 flex items-center gap-2">
              <Star size={18} className="text-yellow-500" />
              Recommandé pour vous
            </h2>
            <Link to="/recommandations" className="text-sm text-blue-600 hover:underline">
              Voir tout
            </Link>
          </div>
          {recos.length === 0 ? (
            <p className="text-sm text-gray-400 text-center py-8">
              Empruntez des livres pour obtenir des recommandations personnalisées.
            </p>
          ) : (
            <div className="flex flex-col gap-3">
              {recos.map((r, i) => (
                <div key={r.livre_id} className="flex items-center gap-3 py-2 border-b last:border-0">
                  <span className="w-7 h-7 rounded-full bg-yellow-100 text-yellow-700
                    flex items-center justify-center text-xs font-bold shrink-0">
                    {i + 1}
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-800 truncate">
                      {r.titre || `Livre #${r.livre_id}`}
                    </p>
                    {r.auteur && <p className="text-xs text-gray-500">{r.auteur}</p>}
                  </div>
                  <div className="text-right shrink-0">
                    <span className={`text-xs px-1.5 py-0.5 rounded ${
                      r.disponible ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'
                    }`}>
                      {r.disponible ? 'Disponible' : 'Indisponible'}
                    </span>
                    <p className="text-xs text-gray-400 mt-0.5">score: {r.score}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
