"""
Tests des méthodes métier des modèles Piccolo.
Ces tests ne nécessitent pas de base de données — on instancie les objets directement.
"""
import pytest
from features.books.tables import Livre


class TestLivreReserver:
    """Tests de la méthode reserver()."""

    def _make_livre(self, disponible=3, total=5):
        livre = Livre()
        livre.quantite_disponible = disponible
        livre.quantite_totale = total
        return livre

    def test_reserver_un_exemplaire(self):
        """Réserver 1 exemplaire décrémente le stock."""
        livre = self._make_livre(disponible=3)
        livre.reserver(1)
        assert livre.quantite_disponible == 2

    def test_reserver_plusieurs_exemplaires(self):
        """Réserver plusieurs exemplaires à la fois."""
        livre = self._make_livre(disponible=3)
        livre.reserver(2)
        assert livre.quantite_disponible == 1

    def test_reserver_dernier_exemplaire(self):
        """On peut réserver le dernier exemplaire."""
        livre = self._make_livre(disponible=1)
        livre.reserver(1)
        assert livre.quantite_disponible == 0

    def test_reserver_stock_insuffisant_leve_erreur(self):
        """Réserver plus que le stock disponible lève une erreur."""
        livre = self._make_livre(disponible=1)
        with pytest.raises(ValueError) as exc:
            livre.reserver(2)
        assert "1" in str(exc.value)

    def test_reserver_stock_zero_leve_erreur(self):
        """Réserver quand stock est à 0 lève une erreur."""
        livre = self._make_livre(disponible=0)
        with pytest.raises(ValueError):
            livre.reserver(1)

    def test_reserver_quantite_zero_leve_erreur(self):
        """La quantité à réserver doit être au moins 1."""
        livre = self._make_livre(disponible=3)
        with pytest.raises(ValueError) as exc:
            livre.reserver(0)
        assert "au moins 1" in str(exc.value)

    def test_reserver_quantite_negative_leve_erreur(self):
        """Une quantité négative lève une erreur."""
        livre = self._make_livre(disponible=3)
        with pytest.raises(ValueError):
            livre.reserver(-1)


class TestLivreRetourner:
    """Tests de la méthode retourner()."""

    def _make_livre(self, disponible=2, total=5):
        livre = Livre()
        livre.quantite_disponible = disponible
        livre.quantite_totale = total
        return livre

    def test_retourner_un_exemplaire(self):
        """Retourner 1 exemplaire incrémente le stock."""
        livre = self._make_livre(disponible=2, total=5)
        livre.retourner(1)
        assert livre.quantite_disponible == 3

    def test_retourner_plusieurs_exemplaires(self):
        """Retourner plusieurs exemplaires à la fois."""
        livre = self._make_livre(disponible=1, total=5)
        livre.retourner(3)
        assert livre.quantite_disponible == 4

    def test_retourner_jusqu_au_stock_total(self):
        """On peut retourner jusqu'à atteindre le stock total."""
        livre = self._make_livre(disponible=4, total=5)
        livre.retourner(1)
        assert livre.quantite_disponible == 5

    def test_retourner_depasse_stock_total_leve_erreur(self):
        """Retourner plus que le stock total lève une erreur."""
        livre = self._make_livre(disponible=5, total=5)
        with pytest.raises(ValueError) as exc:
            livre.retourner(1)
        assert "total" in str(exc.value)

    def test_retourner_quantite_zero_leve_erreur(self):
        """La quantité à retourner doit être au moins 1."""
        livre = self._make_livre(disponible=2, total=5)
        with pytest.raises(ValueError) as exc:
            livre.retourner(0)
        assert "au moins 1" in str(exc.value)


class TestLivreDisponible:
    """Tests de la propriété disponible."""

    def test_disponible_si_stock_positif(self):
        livre = Livre()
        livre.quantite_disponible = 3
        assert livre.disponible is True

    def test_indisponible_si_stock_zero(self):
        livre = Livre()
        livre.quantite_disponible = 0
        assert livre.disponible is False