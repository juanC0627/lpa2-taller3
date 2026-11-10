"""
Tests para la API de Música.
Pruebas unitarias y de integración usando pytest.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from main import app
from musica_api.database import get_session
from musica_api.models import Usuario, Cancion, Favorito


# =============================================================================
# CONFIGURACIÓN DE FIXTURES
# =============================================================================

@pytest.fixture(name="session")
def session_fixture():
    """
    Crea una sesión de base de datos en memoria para cada test.
    Se limpia automáticamente después de cada test.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """
    Crea un cliente de pruebas de FastAPI con la sesión de test.
    """
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="usuario_test")
def usuario_test_fixture(session: Session):
    """Crea un usuario de prueba en la base de datos."""
    usuario = Usuario(nombre="Usuario Test", correo="test@example.com")
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario


@pytest.fixture(name="cancion_test")
def cancion_test_fixture(session: Session):
    """Crea una canción de prueba en la base de datos."""
    cancion = Cancion(
        titulo="Bohemian Rhapsody",
        artista="Queen",
        album="A Night at the Opera",
        duracion=354,
        año=1975,
        genero="Rock"
    )
    session.add(cancion)
    session.commit()
    session.refresh(cancion)
    return cancion


# =============================================================================
# TESTS DE USUARIOS
# =============================================================================

class TestUsuarios:
    """Tests para los endpoints de usuarios."""
    
    def test_listar_usuarios(self, client: TestClient, usuario_test: Usuario):
        """Test para GET /api/usuarios"""
        response = client.get("/api/usuarios")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["correo"] == usuario_test.correo

    def test_crear_usuario(self, client: TestClient):
        """Test para POST /api/usuarios"""
        payload = {"nombre": "Nuevo Usuario", "correo": "nuevo@example.com"}
        response = client.post("/api/usuarios", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == "Nuevo Usuario"
        assert "id" in data

    def test_crear_usuario_correo_duplicado(self, client: TestClient, usuario_test: Usuario):
        """Test para verificar que no se permiten correos duplicados"""
        payload = {"nombre": "Duplicado", "correo": usuario_test.correo}
        response = client.post("/api/usuarios", json=payload)
        assert response.status_code == 400
        assert "correo ya está registrado" in response.json()["detail"]

    def test_obtener_usuario(self, client: TestClient, usuario_test: Usuario):
        """Test para GET /api/usuarios/{id}"""
        response = client.get(f"/api/usuarios/{usuario_test.id}")
        assert response.status_code == 200
        assert response.json()["nombre"] == usuario_test.nombre

    def test_obtener_usuario_no_existe(self, client: TestClient):
        """Test para verificar error 404 con usuario inexistente"""
        response = client.get("/api/usuarios/9999")
        assert response.status_code == 404

    def test_actualizar_usuario(self, client: TestClient, usuario_test: Usuario):
        """Test para PUT /api/usuarios/{id}"""
        payload = {"nombre": "Nombre Actualizado"}
        response = client.put(f"/api/usuarios/{usuario_test.id}", json=payload)
        assert response.status_code == 200
        assert response.json()["nombre"] == "Nombre Actualizado"

    def test_eliminar_usuario(self, client: TestClient, usuario_test: Usuario):
        """Test para DELETE /api/usuarios/{id}"""
        response = client.delete(f"/api/usuarios/{usuario_test.id}")
        assert response.status_code == 200
        assert client.get(f"/api/usuarios/{usuario_test.id}").status_code == 404


# =============================================================================
# TESTS DE CANCIONES
# =============================================================================

class TestCanciones:
    """Tests para los endpoints de canciones."""
    
    def test_listar_canciones(self, client: TestClient, cancion_test: Cancion):
        """Test para GET /api/canciones"""
        response = client.get("/api/canciones")
        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_crear_cancion(self, client: TestClient):
        """Test para POST /api/canciones"""
        payload = {
            "titulo": "Hotel California",
            "artista": "Eagles",
            "album": "Hotel California",
            "duracion": 390,
            "año": 1976,
            "genero": "Rock"
        }
        response = client.post("/api/canciones", json=payload)
        assert response.status_code == 201
        assert response.json()["titulo"] == "Hotel California"

    def test_obtener_cancion(self, client: TestClient, cancion_test: Cancion):
        """Test para GET /api/canciones/{id}"""
        response = client.get(f"/api/canciones/{cancion_test.id}")
        assert response.status_code == 200
        assert response.json()["titulo"] == cancion_test.titulo

    def test_actualizar_cancion(self, client: TestClient, cancion_test: Cancion):
        """Test para PUT /api/canciones/{id}"""
        payload = {"titulo": "Nuevo Titulo"}
        response = client.put(f"/api/canciones/{cancion_test.id}", json=payload)
        assert response.status_code == 200
        assert response.json()["titulo"] == "Nuevo Titulo"

    def test_eliminar_cancion(self, client: TestClient, cancion_test: Cancion):
        """Test para DELETE /api/canciones/{id}"""
        response = client.delete(f"/api/canciones/{cancion_test.id}")
        assert response.status_code == 200
        assert client.get(f"/api/canciones/{cancion_test.id}").status_code == 404

    def test_buscar_canciones(self, client: TestClient, cancion_test: Cancion):
        """Test para GET /api/canciones/buscar"""
        response = client.get("/api/canciones/buscar?titulo=Bohemian")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_buscar_canciones_multiples_filtros(self, client: TestClient, cancion_test: Cancion):
        """Test para búsqueda con múltiples parámetros"""
        response = client.get("/api/canciones/buscar?artista=Queen&genero=Rock")
        assert response.status_code == 200
        assert len(response.json()) == 1


# =============================================================================
# TESTS DE FAVORITOS
# =============================================================================

class TestFavoritos:
    """Tests para los endpoints de favoritos."""
    
    def test_listar_favoritos(self, client: TestClient):
        """Test para GET /api/favoritos"""
        response = client.get("/api/favoritos")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_crear_favorito(self, client: TestClient, usuario_test: Usuario, cancion_test: Cancion):
        """Test para POST /api/favoritos"""
        payload = {"id_usuario": usuario_test.id, "id_cancion": cancion_test.id}
        response = client.post("/api/favoritos", json=payload)
        assert response.status_code == 201
        assert response.json()["id_usuario"] == usuario_test.id

    def test_crear_favorito_duplicado(self, client: TestClient, usuario_test: Usuario, cancion_test: Cancion):
        """Test para verificar que no se permiten favoritos duplicados"""
        payload = {"id_usuario": usuario_test.id, "id_cancion": cancion_test.id}
        client.post("/api/favoritos", json=payload)
        response = client.post("/api/favoritos", json=payload)
        assert response.status_code == 400

    def test_eliminar_favorito(self, client: TestClient, usuario_test: Usuario, cancion_test: Cancion):
        """Test para DELETE /api/favoritos/{id}"""
        payload = {"id_usuario": usuario_test.id, "id_cancion": cancion_test.id}
        fav_resp = client.post("/api/favoritos", json=payload)
        fav_id = fav_resp.json()["id"]
        response = client.delete(f"/api/favoritos/{fav_id}")
        assert response.status_code == 200


# =============================================================================
# TESTS DE INTEGRACIÓN
# =============================================================================

class TestIntegracion:
    """Tests de integración que prueban flujos completos."""
    
    def test_flujo_completo(self, client: TestClient):
        """Test que verifica el flujo completo de la aplicación"""
        # 1. Crear usuario
        u_resp = client.post("/api/usuarios", json={"nombre": "Usuario Flujo", "correo": "flujo@example.com"})
        assert u_resp.status_code == 201
        usuario_id = u_resp.json()["id"]

        # 2. Crear canción
        c_resp = client.post("/api/canciones", json={
            "titulo": "Cancion Flujo", "artista": "Artista Flujo",
            "album": "Album", "duracion": 180, "año": 2022, "genero": "Pop"
        })
        assert c_resp.status_code == 201
        cancion_id = c_resp.json()["id"]

        # 3. Marcar como favorito
        f_resp = client.post("/api/favoritos", json={"id_usuario": usuario_id, "id_cancion": cancion_id})
        assert f_resp.status_code == 201

        # 4. Verificar existencia en lista de favoritos
        favs = client.get("/api/favoritos").json()
        assert any(fav["id_usuario"] == usuario_id and fav["id_cancion"] == cancion_id for fav in favs)


# =============================================================================
# TESTS DE VALIDACIÓN
# =============================================================================

class TestValidacion:
    """Tests para validaciones de datos."""
    
    def test_email_invalido(self, client: TestClient):
        """Test para verificar validación de email"""
        response = client.post("/api/usuarios", json={"nombre": "Invalido", "correo": "correo-no-valido"})
        assert response.status_code == 400

    def test_año_cancion_invalido(self, client: TestClient):
        """Test para verificar validación de año"""
        payload = {
            "titulo": "Futuro", "artista": "Time Traveler",
            "album": "Futuro", "duracion": 180, "año": 2099, "genero": "Electronic"
        }
        response = client.post("/api/canciones", json=payload)
        assert response.status_code == 400

    def test_campos_requeridos(self, client: TestClient):
        """Test para verificar que los campos requeridos son obligatorios"""
        response = client.post("/api/usuarios", json={"nombre": "Incompleto"})
        assert response.status_code == 422