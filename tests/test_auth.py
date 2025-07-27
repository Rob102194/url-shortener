import pytest

# Todas las corutinas de prueba se tratarán como marcadas.
pytestmark = pytest.mark.asyncio

async def test_register_ok(client):
    res = await client.post(
        "/auth/register",
        json={"email": "test@mail.com", "password": "secret"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert "refresh_token" in data

# Prueba de registro con correo electrónico duplicado
async def test_register_duplicate_email(client):
    # Se registra un primer usuario
    await client.post(
        "/auth/register",
        json={"email": "test@mail.com", "password": "secret"},
    )
    # Se intenta registrar con el mismo email
    res = await client.post(
        "/auth/register",
        json={"email": "test@mail.com", "password": "secret"},
    )
    assert res.status_code == 400

# Pruebas de inicio de sesión
async def test_login_ok(client):
    # Se registra un usuario
    await client.post(
        "/auth/register",
        json={"email": "test@mail.com", "password": "secret"},
    )
    # Se inicia sesión
    res = await client.post(
        "/auth/login",
        json={"email": "test@mail.com", "password": "secret"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert "refresh_token" in data

# Prueba de inicio de sesión con contraseña incorrecta
async def test_login_wrong_pwd(client):
    # Se registra un usuario
    await client.post(
        "/auth/register",
        json={"email": "test@mail.com", "password": "secret"},
    )
    # Se inicia sesión con contraseña incorrecta
    res = await client.post(
        "/auth/login",
        json={"email": "test@mail.com", "password": "wrong"},
    )
    assert res.status_code == 401

# Prueba de inicio de sesión con usuario no registrado
async def test_login_user_not_found(client):
    res = await client.post(
        "/auth/login",
        json={"email": "missed@mail.com", "password": "secret"},
    )
    assert res.status_code == 401

# Prueba de refresco de token
async def test_refresh_ok(client):
    # Se registra un usuario
    await client.post(
        "/auth/register",
        json={"email": "test@mail.com", "password": "secret"},
    )
    # Se inicia sesión para obtener un token de actualización
    login_res = await client.post(
        "/auth/login",
        json={"email": "test@mail.com", "password": "secret"},
    )
    refresh_token = login_res.json()["refresh_token"]

    # Se usa el token de actualización
    refresh_res = await client.post(
        "/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert refresh_res.status_code == 200
    data = refresh_res.json()
    assert "access_token" in data
    assert "refresh_token" in data

# Prueba de cierre de sesión
async def test_logout_ok(client):
    # Se registra un usuario
    await client.post(
        "/auth/register",
        json={"email": "test@mail.com", "password": "secret"},
    )
    # Iniciar sesión para obtener un token de actualización
    login_res = await client.post(
        "/auth/login",
        json={"email": "test@mail.com", "password": "secret"},
    )
    refresh_token = login_res.json()["refresh_token"]

    # Logout
    logout_res = await client.post(
        "/auth/logout", json={"refresh_token": refresh_token}
    )
    assert logout_res.status_code == 200

    # Intentar refrescar el token después de cerrar sesión. Esto debería fallar porque el token está en la lista negra
    refresh_res = await client.post(
        "/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert refresh_res.status_code == 401

# Prueba de obtener información del usuario autenticado
async def test_me_ok(client):
    await client.post(
        "/auth/register",
        json={"email": "test@mail.com", "password": "secret"},
    )
    login_res = await client.post(
        "/auth/login",
        json={"email": "test@mail.com", "password": "secret"},
    )
    access_token = login_res.json()["access_token"]

    # Obtener información del usuario autenticado
    me_res = await client.get(
        "/auth/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "test@mail.com"

# Prueba de obtener información del usuario sin autenticación
async def test_login_rate_limit(client):
    await client.post(
        "/auth/register",
        json={"email": "test@mail.com", "password": "secret"},
    )

    # Hacer 5 solicitudes de inicio de sesión 
    for _ in range(5):
        res = await client.post(
            "/auth/login",
            json={"email": "test@mail.com", "password": "secret"},
        )
        assert res.status_code == 200

    # La 6ta solicitud debería ser rate-limited
    res = await client.post(
        "/auth/login",
        json={"email": "test@mail.com", "password": "secret"},
    )
    assert res.status_code == 429

# Prueba de límite de tasa en el endpoint /me
async def test_me_rate_limit(client):
    await client.post(
        "/auth/register",
        json={"email": "test@mail.com", "password": "secret"},
    )
    login_res = await client.post(
        "/auth/login",
        json={"email": "test@mail.com", "password": "secret"},
    )
    access_token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # Hacer 50 solicitudes al endpoint /me
    for i in range(50):
        res = await client.get("/auth/me", headers=headers)
        assert res.status_code == 200, f"Request {i+1} failed"

    # La 51ª solicitud debería ser rate-limited
    res = await client.get("/auth/me", headers=headers)
    assert res.status_code == 429
