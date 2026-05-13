"""
Tests des schemas Pydantic — validation des données.
Ces tests ne nécessitent pas de base de données.
"""
import pytest
from pydantic import ValidationError
from features.books.schemas import LivreIn, DisponibiliteOut, LivrePatchIn


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

    def test_stock_par_defaut(self):
        livre = LivreIn(titre="Test", auteur="Auteur", isbn="9780132350884")
        assert livre.quantite_totale == 1

    def test_stock_personnalise(self):
        livre = LivreIn(titre="Test", auteur="Auteur", isbn="9780132350884", quantite_totale=5)
        assert livre.quantite_totale == 5


class TestDisponibiliteOut:

    def test_disponibilite_out_valide(self):
        data = DisponibiliteOut(
            message="Disponibilité récupérée avec succès.",
            titre="Clean Code",
            isbn="9780132350884",
            quantite_totale=3,
            actif=True,
            couverture_url="",
        )
        assert data.titre == "Clean Code"
        assert data.isbn == "9780132350884"
        assert data.quantite_totale == 3
        assert data.actif is True

    def test_disponibilite_out_couverture_defaut(self):
        data = DisponibiliteOut(
            message="ok",
            titre="Test",
            isbn="9780132350884",
            quantite_totale=1,
            actif=True,
        )
        assert data.couverture_url == ""


class TestLivrePatchIn:

    def test_patch_partiel_valide(self):
        patch = LivrePatchIn(titre="Nouveau titre")
        assert patch.titre == "Nouveau titre"
        assert patch.auteur is None

    def test_patch_vide_valide(self):
        patch = LivrePatchIn()
        assert patch.titre is None
        # ✅ isbn n'existe pas dans LivrePatchIn — c'est intentionnel