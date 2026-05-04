"""
Tests des endpoints HTTP du service Livres.
Utilise le client de test Litestar (sans Docker nécessaire).
"""
import pytest
import pytest_asyncio
from litestar.testing import AsyncTestClient
from app import app


@pytest_asyncio.fixture(scope="function")
async def client():
    async with AsyncTestClient(app=app) as c:
        yield c


class TestHealthCheck:
    """Tests du health check."""

    @pytest.mark.asyncio
    async def test_health_retourne_200(self, client):
        response = await client.get("/health")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_health_contient_service_livres(self, client):
        response = await client.get("/health")
        data = response.json()
        assert data["service"] == "livres"
        assert data["status"] in ("ok", "degraded")
        assert "version" in data
        assert "db" in data


class TestListeLivres:
    """Tests de l'endpoint GET /api/livres/."""

    @pytest.mark.asyncio
    async def test_liste_retourne_200(self, client):
        response = await client.get("/api/livres/")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_liste_structure_paginee(self, client):
        response = await client.get("/api/livres/")
        data = response.json()
        assert "count" in data
        assert "page" in data
        assert "page_size" in data
        assert "results" in data
        assert isinstance(data["results"], list)

    @pytest.mark.asyncio
    async def test_liste_pagination_page_2(self, client):
        response = await client.get("/api/livres/?page=2&page_size=10")
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2
        assert data["page_size"] == 10

    @pytest.mark.asyncio
    async def test_liste_champs_livre(self, client):
        """Chaque livre retourné contient les bons champs."""
        response = await client.get("/api/livres/")
        data = response.json()
        if data["results"]:
            livre = data["results"][0]
            assert "id" in livre
            assert "titre" in livre
            assert "auteur" in livre
            assert "isbn" in livre
            assert "disponible" in livre
            assert "quantite_disponible" in livre
            assert "quantite_totale" in livre


class TestRecherche:
    """Tests de l'endpoint GET /api/livres/search."""

    @pytest.mark.asyncio
    async def test_recherche_par_titre(self, client):
        response = await client.get("/api/livres/search?q=python")
        assert response.status_code == 200
        data = response.json()
        assert "results" in data

    @pytest.mark.asyncio
    async def test_recherche_vide_retourne_tous(self, client):
        response = await client.get("/api/livres/search")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_recherche_inexistante_retourne_zero(self, client):
        # ✅ CORRECTION : utiliser params= pour que le filtre soit bien appliqué
        response = await client.get("/api/livres/search", params={"q": "xyzabcdef123456"})
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["results"] == []

    @pytest.mark.asyncio
    async def test_recherche_par_langue(self, client):
        response = await client.get("/api/livres/search?langue=fr")
        assert response.status_code == 200
        data = response.json()
        for livre in data["results"]:
            assert livre["langue"] == "fr"

    @pytest.mark.asyncio
    async def test_recherche_disponibles(self, client):
        response = await client.get("/api/livres/search?disponible=true")
        assert response.status_code == 200
        data = response.json()
        for livre in data["results"]:
            assert livre["disponible"] is True


class TestDisponibles:
    """Tests de l'endpoint GET /api/livres/disponibles."""

    @pytest.mark.asyncio
    async def test_disponibles_retourne_200(self, client):
        response = await client.get("/api/livres/disponibles")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_disponibles_tous_disponibles(self, client):
        """Tous les livres retournés doivent être disponibles."""
        response = await client.get("/api/livres/disponibles")
        data = response.json()
        for livre in data["results"]:
            assert livre["disponible"] is True
            assert livre["quantite_disponible"] > 0


class TestDetailLivre:
    """Tests de l'endpoint GET /api/livres/{id}."""

    @pytest.mark.asyncio
    async def test_detail_livre_existant(self, client):
        response = await client.get("/api/livres/2")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 2
        assert "titre" in data
        assert "isbn" in data
        assert "disponible" in data
        assert "date_ajout" in data
        assert "date_modification" in data

    @pytest.mark.asyncio
    async def test_detail_livre_inexistant_retourne_404(self, client):
        response = await client.get("/api/livres/99999")
        assert response.status_code == 404


class TestCreerLivre:
    """Tests de l'endpoint POST /api/livres/."""

    @pytest.mark.asyncio
    async def test_creer_livre_valide(self, client):
        nouveau = {
            "titre": "Livre Test Unitaire",
            "auteur": "Auteur Test",
            "isbn": "9782100715671",
            "quantite_totale": 2,
        }
        response = await client.post("/api/livres/", json=nouveau)
        assert response.status_code in (201, 409)

    @pytest.mark.asyncio
    async def test_creer_livre_isbn_invalide(self, client):
        nouveau = {
            "titre": "Test",
            "auteur": "Auteur",
            "isbn": "1234567890123",
        }
        response = await client.post("/api/livres/", json=nouveau)
        # ✅ CORRECTION : Litestar retourne 400 pour les erreurs de validation Pydantic
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_creer_livre_isbn_duplique_retourne_409(self, client):
        """Un ISBN déjà existant retourne 409 Conflict."""
        duplique = {
            "titre": "Clean Code Copie",
            "auteur": "Robert C. Martin",
            "isbn": "9780132350884",
        }
        response = await client.post("/api/livres/", json=duplique)
        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_creer_livre_sans_titre_retourne_400(self, client):
        incomplet = {"auteur": "Auteur", "isbn": "9780132350884"}
        response = await client.post("/api/livres/", json=incomplet)
        # ✅ CORRECTION : Litestar retourne 400 pour les champs manquants
        assert response.status_code == 400


class TestSupprimerLivre:
    """Tests de l'endpoint DELETE /api/livres/{id}."""

    @pytest.mark.asyncio
    async def test_supprimer_livre_existant_retourne_204(self, client):
        # ✅ CORRECTION : utiliser le livre 5 pour ne pas perturber les autres tests
        response = await client.delete("/api/livres/5")
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_supprimer_livre_inexistant_retourne_404(self, client):
        response = await client.delete("/api/livres/99999")
        assert response.status_code == 404


class TestCategories:
    """Tests des endpoints catégories."""

    @pytest.mark.asyncio
    async def test_lister_categories_retourne_200(self, client):
        response = await client.get("/api/categories/")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_categories_contiennent_nombre_livres(self, client):
        response = await client.get("/api/categories/")
        data = response.json()
        assert isinstance(data, list)
        if data:
            assert "nombre_livres" in data[0]
            assert "nom" in data[0]

    @pytest.mark.asyncio
    async def test_detail_categorie_existante(self, client):
        response = await client.get("/api/categories/1")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_detail_categorie_inexistante_retourne_404(self, client):
        response = await client.get("/api/categories/99999")
        assert response.status_code == 404


class TestDisponibilite:
    """Tests de l'endpoint POST /api/livres/{id}/disponibilite."""

    @pytest.mark.asyncio
    async def test_reserver_exemplaire(self, client):
        # ✅ CORRECTION : utiliser livre 10 (pas le 1 utilisé dans d'autres tests)
        detail = await client.get("/api/livres/10")
        stock_initial = detail.json()["quantite_disponible"]

        response = await client.post(
            "/api/livres/10/disponibilite",
            json={"action": "reserver", "quantite": 1}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["quantite_disponible"] == stock_initial - 1

    @pytest.mark.asyncio
    async def test_retourner_exemplaire(self, client):
        await client.post(
            "/api/livres/3/disponibilite",
            json={"action": "reserver", "quantite": 1}
        )
        response = await client.post(
            "/api/livres/3/disponibilite",
            json={"action": "retourner", "quantite": 1}
        )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_reserver_stock_insuffisant_retourne_400(self, client):
        # ✅ CORRECTION : utiliser livre 10 (pas le 1 qui peut être supprimé)
        response = await client.post(
            "/api/livres/10/disponibilite",
            json={"action": "reserver", "quantite": 9999}
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_action_invalide_retourne_400(self, client):
        # ✅ CORRECTION : Litestar retourne 400 pas 422 pour les erreurs Pydantic
        response = await client.post(
            "/api/livres/10/disponibilite",
            json={"action": "supprimer", "quantite": 1}
        )
        assert response.status_code == 400