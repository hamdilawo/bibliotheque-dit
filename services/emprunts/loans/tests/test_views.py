"""
Tests du service Emprunts — Bibliothèque DIT
=============================================
Tous les appels inter-services (Livres, Utilisateurs) sont mockés
afin de tester le service de manière isolée.

Lancer : python manage.py test loans.tests
"""
from datetime import date, timedelta
from unittest.mock import patch

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from loans.models import Emprunt
from loans.client import ServiceException


# ─── Données de test partagées ────────────────────────────────────────────────

LIVRE_OK = {
    'id': 1, 'titre': 'Clean Code', 'isbn': '9780132350884',
    'auteur': 'R. Martin', 'disponible': True,
}
LIVRE_INDISPO = {**LIVRE_OK, 'disponible': False}

UTILISATEUR_OK = {
    'id': 1, 'nom_complet': 'Moussa Ba', 'numero_carte': 'ETU2026001',
    'type_utilisateur': 'ETUDIANT', 'peut_emprunter': True,
}
UTILISATEUR_SUSPENDU = {**UTILISATEUR_OK, 'peut_emprunter': False}


def creer_emprunt(utilisateur_id=1, livre_id=1, statut='EN_COURS',
                  jours_retard=0, penalite=0, date_offset_jours=None):
    """Helper : crée un emprunt en base avec les paramètres donnés."""
    aujourd_hui = date.today()
    date_retour = aujourd_hui + timedelta(days=14)
    if date_offset_jours is not None:
        date_retour = aujourd_hui - timedelta(days=date_offset_jours)

    return Emprunt.objects.create(
        utilisateur_id=utilisateur_id,
        livre_id=livre_id,
        utilisateur_nom='Moussa Ba',
        utilisateur_carte='ETU2026001',
        livre_titre='Clean Code',
        livre_isbn='9780132350884',
        livre_auteur='R. Martin',
        date_retour_prevue=date_retour,
        statut=statut,
        jours_retard=jours_retard,
        penalite_fcfa=penalite,
    )


# ─── Tests : Modèle ──────────────────────────────────────────────────────────

class EmpruntModelTest(TestCase):

    def test_duree_par_defaut_etudiant(self):
        self.assertEqual(Emprunt.get_duree_par_defaut('ETUDIANT'), 14)

    def test_duree_par_defaut_professeur(self):
        self.assertEqual(Emprunt.get_duree_par_defaut('PROFESSEUR'), 30)

    def test_duree_par_defaut_inconnu(self):
        self.assertEqual(Emprunt.get_duree_par_defaut('INCONNU'), 14)

    def test_est_en_retard_true(self):
        e = creer_emprunt(date_offset_jours=5)
        self.assertTrue(e.est_en_retard)

    def test_est_en_retard_false_retourne(self):
        e = creer_emprunt(statut='RETOURNE', date_offset_jours=5)
        self.assertFalse(e.est_en_retard)

    def test_jours_restants_retourne(self):
        e = creer_emprunt(statut='RETOURNE')
        self.assertEqual(e.jours_restants, 0)

    def test_calculer_retard(self):
        e = creer_emprunt(date_offset_jours=3)
        e.calculer_retard()
        e.refresh_from_db()
        self.assertEqual(e.jours_retard, 3)
        self.assertEqual(e.penalite_fcfa, 600)
        self.assertEqual(e.statut, 'EN_RETARD')

    def test_str(self):
        e = creer_emprunt()
        self.assertIn('Clean Code', str(e))
        self.assertIn('Moussa Ba', str(e))


# ─── Tests : Création d'emprunt ──────────────────────────────────────────────

class EmpruntCreationTest(APITestCase):

    @patch('loans.views.LivresClient.reserver_livre', return_value={})
    @patch('loans.views.UtilisateursClient.incrementer_emprunts', return_value={})
    @patch('loans.views.UtilisateursClient.get_utilisateur', return_value=UTILISATEUR_OK)
    @patch('loans.views.LivresClient.get_livre', return_value=LIVRE_OK)
    def test_creer_emprunt_succes(self, mock_livre, mock_user, mock_incr, mock_resa):
        response = self.client.post('/api/emprunts/emprunter/', {
            'utilisateur_id': 1, 'livre_id': 1
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Emprunt.objects.count(), 1)
        e = Emprunt.objects.first()
        self.assertEqual(e.statut, 'EN_COURS')
        self.assertEqual(e.livre_titre, 'Clean Code')

    @patch('loans.views.UtilisateursClient.get_utilisateur', return_value=UTILISATEUR_SUSPENDU)
    @patch('loans.views.LivresClient.get_livre', return_value=LIVRE_OK)
    def test_creer_emprunt_utilisateur_suspendu(self, mock_livre, mock_user):
        response = self.client.post('/api/emprunts/emprunter/', {
            'utilisateur_id': 1, 'livre_id': 1
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('loans.views.UtilisateursClient.get_utilisateur', return_value=UTILISATEUR_OK)
    @patch('loans.views.LivresClient.get_livre', return_value=LIVRE_INDISPO)
    def test_creer_emprunt_livre_indisponible(self, mock_livre, mock_user):
        response = self.client.post('/api/emprunts/emprunter/', {
            'utilisateur_id': 1, 'livre_id': 1
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('loans.views.UtilisateursClient.get_utilisateur', return_value=UTILISATEUR_OK)
    @patch('loans.views.LivresClient.get_livre', return_value=LIVRE_OK)
    def test_creer_emprunt_livre_deja_emprunte(self, mock_livre, mock_user):
        creer_emprunt(utilisateur_id=2, livre_id=1, statut='EN_COURS')
        response = self.client.post('/api/emprunts/emprunter/', {
            'utilisateur_id': 1, 'livre_id': 1
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('loans.views.LivresClient.get_livre',
           side_effect=ServiceException('Service Livres indisponible.', 503))
    def test_creer_emprunt_service_livres_down(self, mock_livre):
        response = self.client.post('/api/emprunts/emprunter/', {
            'utilisateur_id': 1, 'livre_id': 1
        }, format='json')
        self.assertIn(response.status_code, [400, 503])


# ─── Tests : Retour d'un livre ───────────────────────────────────────────────

class RetourLivreTest(APITestCase):

    @patch('loans.views.LivresClient.retourner_livre', return_value={})
    @patch('loans.views.UtilisateursClient.decrementer_emprunts', return_value={})
    def test_retour_succes_sans_retard(self, mock_decr, mock_retour):
        e = creer_emprunt()
        response = self.client.post(f'/api/emprunts/{e.pk}/retourner/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        e.refresh_from_db()
        self.assertEqual(e.statut, 'RETOURNE')
        self.assertEqual(e.jours_retard, 0)
        self.assertIn('Merci', response.data.get('message', ''))

    @patch('loans.views.LivresClient.retourner_livre', return_value={})
    @patch('loans.views.UtilisateursClient.decrementer_emprunts', return_value={})
    def test_retour_avec_retard(self, mock_decr, mock_retour):
        e = creer_emprunt(date_offset_jours=5)
        response = self.client.post(f'/api/emprunts/{e.pk}/retourner/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        e.refresh_from_db()
        self.assertEqual(e.statut, 'RETOURNE')
        self.assertEqual(e.jours_retard, 5)
        self.assertEqual(float(e.penalite_fcfa), 1000.0)
        self.assertIn('retard', response.data.get('message', ''))

    def test_retour_double_impossible(self):
        e = creer_emprunt(statut='RETOURNE')
        e.date_retour_effective = date.today()
        e.save()
        response = self.client.post(f'/api/emprunts/{e.pk}/retourner/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retour_emprunt_inexistant(self):
        response = self.client.post('/api/emprunts/9999/retourner/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# ─── Tests : Prolongation ────────────────────────────────────────────────────

class ProlongationTest(APITestCase):

    def test_prolongation_succes(self):
        e = creer_emprunt()
        ancienne_date = e.date_retour_prevue
        response = self.client.post(
            f'/api/emprunts/{e.pk}/prolonger/',
            {'jours_supplementaires': 7},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        e.refresh_from_db()
        self.assertEqual(e.date_retour_prevue, ancienne_date + timedelta(days=7))

    def test_prolongation_remet_en_cours_si_retard(self):
        e = creer_emprunt(statut='EN_RETARD', date_offset_jours=2)
        response = self.client.post(
            f'/api/emprunts/{e.pk}/prolonger/',
            {'jours_supplementaires': 7},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        e.refresh_from_db()
        self.assertEqual(e.statut, 'EN_COURS')

    def test_limite_deux_prolongations(self):
        e = creer_emprunt()
        url = f'/api/emprunts/{e.pk}/prolonger/'
        self.client.post(url, {'jours_supplementaires': 7}, format='json')
        self.client.post(url, {'jours_supplementaires': 7}, format='json')
        response = self.client.post(url, {'jours_supplementaires': 7}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_prolongation_emprunt_retourne_impossible(self):
        e = creer_emprunt(statut='RETOURNE')
        response = self.client.post(
            f'/api/emprunts/{e.pk}/prolonger/',
            {'jours_supplementaires': 7},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_prolongation_jours_invalides(self):
        e = creer_emprunt()
        response = self.client.post(
            f'/api/emprunts/{e.pk}/prolonger/',
            {'jours_supplementaires': 0},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# ─── Tests : Historique utilisateur ─────────────────────────────────────────

class HistoriqueTest(APITestCase):

    def setUp(self):
        creer_emprunt(utilisateur_id=1, livre_id=1, statut='RETOURNE')
        creer_emprunt(utilisateur_id=1, livre_id=2, statut='EN_COURS')
        creer_emprunt(utilisateur_id=2, livre_id=3, statut='RETOURNE')

    def test_historique_filtre_par_utilisateur(self):
        response = self.client.get('/api/emprunts/historique/?utilisateur_id=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_historique_sans_utilisateur_id(self):
        response = self.client.get('/api/emprunts/historique/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_historique_utilisateur_sans_emprunts(self):
        response = self.client.get('/api/emprunts/historique/?utilisateur_id=999')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)


# ─── Tests : Retards ─────────────────────────────────────────────────────────

class RetardsTest(APITestCase):

    def test_retards_detectes_automatiquement(self):
        creer_emprunt(utilisateur_id=1, livre_id=1, statut='EN_COURS', date_offset_jours=3)
        creer_emprunt(utilisateur_id=2, livre_id=2, statut='EN_COURS', date_offset_jours=1)
        creer_emprunt(utilisateur_id=3, livre_id=3, statut='EN_COURS')
        response = self.client.get('/api/emprunts/retards/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_retards'], 2)

    def test_emprunt_retourne_absent_des_retards(self):
        creer_emprunt(statut='RETOURNE', date_offset_jours=5)
        response = self.client.get('/api/emprunts/retards/')
        self.assertEqual(response.data['total_retards'], 0)


# ─── Tests : Statistiques ────────────────────────────────────────────────────

class StatistiquesTest(APITestCase):

    def setUp(self):
        creer_emprunt(utilisateur_id=1, livre_id=1, statut='EN_COURS')
        creer_emprunt(utilisateur_id=1, livre_id=2, statut='EN_RETARD', jours_retard=3, penalite=600)
        creer_emprunt(utilisateur_id=2, livre_id=3, statut='RETOURNE')

    def test_statistiques_globales(self):
        response = self.client.get('/api/emprunts/statistiques/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_emprunts'], 3)
        self.assertEqual(response.data['en_cours'], 1)
        self.assertEqual(response.data['en_retard'], 1)
        self.assertEqual(response.data['retournes'], 1)
        self.assertEqual(float(response.data['penalites_totales_fcfa']), 600.0)


# ─── Tests : Export CSV ──────────────────────────────────────────────────────

class ExportCSVTest(APITestCase):

    def setUp(self):
        e = creer_emprunt(statut='RETOURNE')
        e.date_retour_effective = date.today()
        e.save()
        creer_emprunt(statut='EN_COURS')

    def test_export_csv_format(self):
        response = self.client.get('/api/emprunts/export_csv/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('text/csv', response['Content-Type'])
        content = response.content.decode('utf-8')
        self.assertIn('utilisateur_id', content)
        self.assertIn('livre_id', content)

    def test_export_csv_seulement_retournes(self):
        response = self.client.get('/api/emprunts/export_csv/')
        content = response.content.decode('utf-8')
        lignes = [l for l in content.strip().split('\n') if l]
        self.assertEqual(len(lignes), 2)