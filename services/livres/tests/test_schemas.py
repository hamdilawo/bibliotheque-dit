"""
Tests des schemas Pydantic — validation des données.
Ces tests ne nécessitent pas de base de données.
"""
import pytest
from pydantic import ValidationError
from features.books.schemas import LivreIn, DisponibiliteIn, LivrePatchIn


class TestValidationISBN:
    """Tests de la validation ISBN-13."""

    def test_isbn_valide(self):
        """Un ISBN-13 valide est accepté."""
        livre = LivreIn(
            titre="Clean Code",
            auteur="Robert C. Martin",
            isbn="9780132350884",
        )
        assert livre.isbn == "9780132350884"

    def test_isbn_avec_tirets_accepte(self):
        """Les tirets sont automatiquement supprimés."""
        livre = LivreIn(
            titre="Test",
            auteur="Auteur",
            isbn="978-0-13-235088-4",
        )
        assert livre.isbn == "9780132350884"

    def test_isbn_trop_court_rejete(self):
        """Un ISBN de moins de 13 chiffres est rejeté."""
        with pytest.raises(ValidationError) as exc:
            LivreIn(titre="Test", auteur="Auteur", isbn="978013235088")
        assert "13 chiffres" in str(exc.value)

    def test_isbn_trop_long_rejete(self):
        """Un ISBN de plus de 13 chiffres est rejeté."""
        with pytest.raises(ValidationError) as exc:
            LivreIn(titre="Test", auteur="Auteur", isbn="97801323508840")
        assert "13 chiffres" in str(exc.value)

    def test_isbn_avec_lettres_rejete(self):
        """Un ISBN contenant des lettres est rejeté."""
        with pytest.raises(ValidationError) as exc:
            LivreIn(titre="Test", auteur="Auteur", isbn="978013235088X")
        assert "chiffres" in str(exc.value)

    def test_isbn_cle_controle_invalide_rejete(self):
        """Un ISBN avec une mauvaise clé de contrôle est rejeté."""
        with pytest.raises(ValidationError) as exc:
            LivreIn(titre="Test", auteur="Auteur", isbn="9780132350885")
        assert "clé de contrôle" in str(exc.value)


class TestValidationAnnee:
    """Tests de la validation de l'année de publication."""

    def test_annee_valide(self):
        """Une année valide est acceptée."""
        livre = LivreIn(
            titre="Test", auteur="Auteur",
            isbn="9780132350884", annee_publication=2008
        )
        assert livre.annee_publication == 2008

    def test_annee_trop_ancienne_rejete(self):
        """Une année avant 1000 est rejetée."""
        with pytest.raises(ValidationError) as exc:
            LivreIn(
                titre="Test", auteur="Auteur",
                isbn="9780132350884", annee_publication=999
            )
        assert "1000" in str(exc.value)

    def test_annee_future_rejetee(self):
        """Une année dans le futur est rejetée."""
        with pytest.raises(ValidationError) as exc:
            LivreIn(
                titre="Test", auteur="Auteur",
                isbn="9780132350884", annee_publication=2099
            )
        assert "dépasser" in str(exc.value)

    def test_annee_none_acceptee(self):
        """L'année peut être absente (None)."""
        livre = LivreIn(
            titre="Test", auteur="Auteur",
            isbn="9780132350884", annee_publication=None
        )
        assert livre.annee_publication is None


class TestValidationStock:
    """Tests de la cohérence des stocks."""

    def test_stock_coherent(self):
        """quantite_disponible <= quantite_totale est accepté."""
        livre = LivreIn(
            titre="Test", auteur="Auteur",
            isbn="9780132350884",
            quantite_totale=5, quantite_disponible=3
        )
        assert livre.quantite_disponible == 3

    def test_stock_disponible_par_defaut(self):
        """Sans quantite_disponible, elle prend la valeur de quantite_totale."""
        livre = LivreIn(
            titre="Test", auteur="Auteur",
            isbn="9780132350884", quantite_totale=5
        )
        assert livre.quantite_disponible == 5

    def test_stock_incoerent_rejete(self):
        """quantite_disponible > quantite_totale est rejeté."""
        with pytest.raises(ValidationError) as exc:
            LivreIn(
                titre="Test", auteur="Auteur",
                isbn="9780132350884",
                quantite_totale=3, quantite_disponible=5
            )
        assert "dépasser" in str(exc.value)


class TestValidationDisponibilite:
    """Tests du schema DisponibiliteIn."""

    def test_action_reserver_valide(self):
        data = DisponibiliteIn(action="reserver", quantite=1)
        assert data.action == "reserver"

    def test_action_retourner_valide(self):
        data = DisponibiliteIn(action="retourner", quantite=2)
        assert data.quantite == 2

    def test_action_invalide_rejetee(self):
        with pytest.raises(ValidationError):
            DisponibiliteIn(action="supprimer", quantite=1)

    def test_quantite_zero_rejetee(self):
        with pytest.raises(ValidationError):
            DisponibiliteIn(action="reserver", quantite=0)

    def test_quantite_negative_rejetee(self):
        with pytest.raises(ValidationError):
            DisponibiliteIn(action="reserver", quantite=-1)


class TestLivrePatchIn:
    """Tests du schema de modification partielle."""

    def test_patch_partiel_valide(self):
        """On peut modifier seulement le titre."""
        patch = LivrePatchIn(titre="Nouveau titre")
        assert patch.titre == "Nouveau titre"
        assert patch.auteur is None

    def test_patch_vide_valide(self):
        """Un patch vide est valide."""
        patch = LivrePatchIn()
        assert patch.titre is None