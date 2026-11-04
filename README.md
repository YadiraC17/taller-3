# FINTRACK

Aplicación web de finanzas personales con API REST Flask, SQLite, autenticación JWT y frontend HTML/CSS/JavaScript.

## Requisitos

- Python 3.11.
- Navegador moderno.
- Windows, macOS o Linux.

## Instalación en Windows

Abre PowerShell en la carpeta `backend` y ejecuta:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edita `backend/.env` y establece dos claves largas y aleatorias para `SECRET_KEY` y `JWT_SECRET_KEY`. La base predeterminada queda en `backend/instance/fintrack.db`; no se necesita configurar un servidor de base de datos.

## Crear o actualizar la base de datos

Desde `backend`:

```powershell
.\.venv\Scripts\flask.exe --app run db upgrade
```

Las migraciones versionadas están en `backend/migrations`. Al cambiar modelos, genera una migración con `flask --app run db migrate -m "Descripción del cambio"`, revísala y aplícala con `flask --app run db upgrade`.

## Iniciar la aplicación

Abre dos terminales desde la raíz del proyecto.

Terminal 1, iniciar la API:

```powershell
cd backend
.\.venv\Scripts\python.exe run.py
```

La API queda en `http://127.0.0.1:5000`; `http://127.0.0.1:5000/` es la comprobación de estado.

Terminal 2, servir el frontend:

```powershell
python -m http.server 5500 --directory frontend
```

Abre `http://127.0.0.1:5500`. El cliente usa `http://127.0.0.1:5000/api` por defecto. Se puede cambiar guardando otra URL base en `localStorage` como `fintrack_api_url`.

## Pruebas

Desde `backend`:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Las pruebas usan SQLite en memoria y no modifican la base de desarrollo.

## Módulos

- Registro, inicio de sesión y consulta de usuario mediante JWT.
- CRUD de categorías, transacciones y presupuestos con aislamiento por usuario.
- Validación de monedas PEN/USD y montos decimales.
- Seguimiento de presupuestos y reportes mensuales calculados en el backend.
- Interfaz adaptable que consume los endpoints propios con Fetch API.

La documentación de endpoints está en [documentacion/API.md](documentacion/API.md), el modelo de datos en [documentacion/MODELO_DATOS.md](documentacion/MODELO_DATOS.md), el [control de cumplimiento](documentacion/CONTROL_CUMPLIMIENTO.md) y el resumen técnico en [documentacion/DOCUMENTACION_TECNICA.md](documentacion/DOCUMENTACION_TECNICA.md). La colección manual está en [documentacion/FINTRACK.postman_collection.json](documentacion/FINTRACK.postman_collection.json).

Para generar el PDF técnico desde la raíz del proyecto:

```powershell
python -m pip install -r documentacion/requirements.txt
python documentacion/generar_pdf.py
```

El archivo se genera en `documentacion/DOCUMENTACION_TECNICA.pdf` con carátula y hasta cinco páginas de contenido.