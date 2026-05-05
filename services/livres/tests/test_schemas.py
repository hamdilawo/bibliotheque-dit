"""
Tests des schemas Pydantic — validation des données.
Ces tests ne nécessitent pas de base de données.
"""
import pytest
from pydantic import ValidationError
from features.books.schemas import LivreIn, DisponibiliteIn, LivrePatchIn


class TestValidationISBN:

    def test_isbn_valide(self):
        livre = LivreIn(titre="Clean Code", auteur="Robert C. Martin", isbn="9780132350884")
        assert livre.isbn == "9780132350884"

    def test_isbn_avec_tirets_accepte(self):
        livre = LivreIn(titre="Test", auteur="Auteur", isbn="978-0-13-235088-4")
        assert livre.isbn == "9780132350884"

    def test_isbn_trop_court_rejete(self):
        with pytest.raises(ValidationError) as exc:
            LivreIn(titre="Test", auteur="Auteur", isbn="978013235088")
        assert "13 chiffres" in str(exc.value)

    def test_isbn_trop_long_rejete(self):
        with pytest.raises(ValidationError) as exc:
            LivreIn(titre="Test", auteur="Auteur", isbn="97801323508840")
        assert "13 chiffres" in str(exc.value)

    def test_isbn_avec_lettres_rejete(self):
        with pytest.raises(ValidationError) as exc:
            LivreIn(titre="Test", auteur="Auteur", isbn="978013235088X")
        assert "chiffres" in str(exc.value)

    def test_isbn_cle_controle_invalide_rejete(self):
        with pytest.raises(ValidationError) as exc:
            LivreIn(titre="Test", auteur="Auteur", isbn="9780132350885")
        assert "clé de contrôle" in str(exc.value)


class TestValidationAnnee:

    def test_annee_valide(self):
        livre = LivreIn(titre="Test", auteur="Auteur", isbn="9780132350884", annee_publication=2008)
        assert livre.annee_publication == 2008

    def test_annee_trop_ancienne_rejete(self):
        with pytest.raises(ValidationError) as exc:
            LivreIn(titre="Test", auteur="Auteur", isbn="9780132350884", annee_publication=999)
        assert "1000" in str(exc.value)

    def test_annee_future_rejetee(self):
        with pytest.raises(ValidationError) as exc:
            LivreIn(titre="Test", auteur="Auteur", isbn="9780132350884", annee_publication=2099)
        assert "dépasser" in str(exc.value)

    def test_annee_none_acceptee(self):
        livre = LivreIn(titre="Test", auteur="Auteur", isbn="9780132350884", annee_publication=None)
        assert livre.annee_publication is None


class TestValidationStock:

    def test_stock_coherent(self):
        livre = LivreIn(titre="Test", auteur="Auteur", isbn="9780132350884",
                        quantite_totale=5, quantite_disponible=3)
        assert livre.quantite_disponible == 3

    def test_stock_disponible_par_defaut(self):
        livre = LivreIn(titre="Test", auteur="Auteur", isbn="9780132350884", quantite_totale=5)
        assert livre.quantite_disponible == 5

    def test_stock_incoerent_rejete(self):
        with pytest.raises(ValidationError) as exc:
            LivreIn(titre="Test", auteur="Auteur", isbn="9780132350884",
                    quantite_totale=3, quantite_disponible=5)
        assert "dépasser" in str(exc.value)


class TestValidationDisponibilite:

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

    def test_patch_partiel_valide(self):
        patch = LivrePatchIn(titre="Nouveau titre")
        assert patch.titre == "Nouveau titre"
        assert patch.auteur is None

    def test_patch_vide_valide(self):
        patch = LivrePatchIn()
        assert patch.titre is None
        # ✅ isbn n'existe pas dans LivrePatchIn — c'est intentionnel