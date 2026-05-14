import axios from 'axios';

const LIVRES_URL    = process.env.REACT_APP_LIVRES_URL    || 'http://localhost:8001';
const USERS_URL     = process.env.REACT_APP_USERS_URL     || 'http://localhost:8002';
const EMPRUNTS_URL  = process.env.REACT_APP_EMPRUNTS_URL  || 'http://localhost:8003';
const RECO_URL      = process.env.REACT_APP_RECO_URL      || 'http://localhost:8004';

const makeClient = (baseURL) => {
  const client = axios.create({ baseURL, timeout: 10000 });
  client.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  });
  client.interceptors.response.use(
    (res) => res,
    (err) => {
      if (err.response?.status === 401) {
        localStorage.removeItem('token');
        window.location.href = '/login';
      }
      return Promise.reject(err);
    }
  );
  return client;
};

export const livresApi    = makeClient(LIVRES_URL);
export const usersApi     = makeClient(USERS_URL);
export const empruntsApi  = makeClient(EMPRUNTS_URL);
export const recoApi      = makeClient(RECO_URL);

// ── Livres ──────────────────────────────────────────────────────────
export const livresService = {
  lister:       (params) => livresApi.get('/api/livres/', { params }),
  detail:       (id)     => livresApi.get(`/api/livres/${id}/`),
  creer:        (data)   => livresApi.post('/api/livres/', data),
  modifier:     (id, d)  => livresApi.put(`/api/livres/${id}/`, d),
  supprimer:    (id)     => livresApi.delete(`/api/livres/${id}/`),
  rechercher:   (params) => livresApi.get('/api/livres/search/', { params }),
  disponibles:  ()       => livresApi.get('/api/livres/disponibles/'),
  categories:   ()       => livresApi.get('/api/categories/'),
};

// ── Utilisateurs ────────────────────────────────────────────────────
export const usersService = {
  login:        (data)   => usersApi.post('/api/auth/token/', data),
  lister:       (params) => usersApi.get('/api/utilisateurs/', { params }),
  detail:       (id)     => usersApi.get(`/api/utilisateurs/${id}/`),
  creer:        (data)   => usersApi.post('/api/utilisateurs/', data),
  modifier:     (id, d)  => usersApi.put(`/api/utilisateurs/${id}/`, d),
  supprimer:    (id)     => usersApi.delete(`/api/utilisateurs/${id}/`),
  rechercher:   (params) => usersApi.get('/api/utilisateurs/search/', { params }),
  statistiques: ()       => usersApi.get('/api/utilisateurs/statistiques/'),
};

// ── Emprunts ────────────────────────────────────────────────────────
export const empruntsService = {
  lister:       (params) => empruntsApi.get('/api/emprunts/', { params }),
  detail:       (id)     => empruntsApi.get(`/api/emprunts/${id}/`),
  emprunter:    (data)   => empruntsApi.post('/api/emprunts/emprunter/', data),
  retourner:    (id, d)  => empruntsApi.post(`/api/emprunts/${id}/retourner/`, d),
  historique:   (params) => empruntsApi.get('/api/emprunts/historique/', { params }),
  retards:      ()       => empruntsApi.get('/api/emprunts/retards/'),
  statistiques: ()       => empruntsApi.get('/api/emprunts/statistiques/'),
  exportCsv:    ()       => empruntsApi.get('/api/emprunts/export_csv/', { responseType: 'blob' }),
};

// ── Recommandations ─────────────────────────────────────────────────
export const recoService = {
  recommandations: (userId, n = 5) => recoApi.get(`/recommandation/${userId}`, { params: { n } }),
  livreSimilaire:  (refIsbn, n = 5) => recoApi.get('/livre_similaire', { params: { ref_isbn: refIsbn, n } }),
  entrainer:       ()              => recoApi.post('/train'),
  metriques:       ()              => recoApi.get('/metric'),
  populaires:      (n = 10)        => recoApi.get('/popular', { params: { n } }),
  health:          ()              => recoApi.get('/health'),
};
