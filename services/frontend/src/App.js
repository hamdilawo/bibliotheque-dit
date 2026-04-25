import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './context/AuthContext';
import Navbar from './components/Navbar';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import LivresPage from './pages/LivresPage';
import EmpruntsPage from './pages/EmpruntsPage';
import UtilisateursPage from './pages/UtilisateursPage';
import RecommandationsPage from './pages/RecommandationsPage';

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="flex justify-center items-center h-screen text-gray-400">Chargement...</div>;
  return user ? children : <Navigate to="/login" />;
}

function Layout({ children }) {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main>{children}</main>
    </div>
  );
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/" element={
        <ProtectedRoute>
          <Layout><DashboardPage /></Layout>
        </ProtectedRoute>
      } />
      <Route path="/livres" element={
        <ProtectedRoute>
          <Layout><LivresPage /></Layout>
        </ProtectedRoute>
      } />
      <Route path="/emprunts" element={
        <ProtectedRoute>
          <Layout><EmpruntsPage /></Layout>
        </ProtectedRoute>
      } />
      <Route path="/utilisateurs" element={
        <ProtectedRoute>
          <Layout><UtilisateursPage /></Layout>
        </ProtectedRoute>
      } />
      <Route path="/recommandations" element={
        <ProtectedRoute>
          <Layout><RecommandationsPage /></Layout>
        </ProtectedRoute>
      } />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
        <Toaster position="top-right" toastOptions={{ duration: 3000 }} />
      </BrowserRouter>
    </AuthProvider>
  );
}
