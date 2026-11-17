# FINTRACK API Server

Backend de finanzas personales. El servidor REST Flask usa SQLite en desarrollo y puede conectarse a PostgreSQL en la nube; los clientes, incluido el APK Android, consumen la API y no contienen la lógica financiera.

## Requisitos

- Python 3.11.
- Windows PowerShell.

## Instalación

Desde la raíz del repositorio:

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Configura `SECRET_KEY` y `JWT_SECRET_KEY` en `backend/.env` con valores aleatorios privados. No subas `.env` al repositorio. SQLite guarda la información en `backend/instance/fintrack.db`.

## Inicializar la base de datos

Desde `backend`:

```powershell
.\.venv\Scripts\flask.exe --app run db upgrade
```

Las migraciones están en `backend/migrations`; las claves foráneas de SQLite se activan al abrir conexiones.

## Iniciar para clientes en la red local

En la laptop servidor, desde `backend`:

```powershell
.\.venv\Scripts\python.exe run.py
```

Por defecto, `run.py` escucha en `0.0.0.0:5000`, lo que permite conexiones entrantes por las interfaces de red de la laptop. Configura `FLASK_HOST` y `FLASK_PORT` en `backend/.env` si necesitas cambiarlo. Autoriza TCP/5000 en el Firewall de Windows para redes privadas. Los teléfonos deben estar en una red que pueda alcanzar la laptop y usar `http://<IPv4-de-la-laptop>:5000/api`. La ruta `http://<IPv4-de-la-laptop>:5000/` devuelve el estado del servicio.

No expongas el servidor de desarrollo de Flask directamente a Internet. Para uso público se necesita HTTPS, un servidor WSGI de producción, secretos adecuados y configuración de red segura.

## API disponible

- Autenticación: registro, login y perfil JWT.
- Categorías: CRUD por usuario.
- Transacciones: CRUD y filtros por tipo, categoría, moneda y fechas.
- Presupuestos: CRUD y seguimiento de gasto acumulado.
- Reportes del servidor: resumen, gastos por categoría y evolución mensual, con PEN/USD separados.

Las rutas usan el prefijo `/api`; las operaciones privadas requieren `Authorization: Bearer <JWT>`. El cierre de sesión revoca el JWT en el servidor. El listado de transacciones devuelve hasta 50 elementos por defecto; admite `page` y `per_page` (máximo 100) y añade metadatos de paginación en `pagination`, conservando `data` como arreglo. Los cálculos de reportes y presupuestos se hacen en el servidor.

## Pruebas

Desde `backend`:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Las pruebas usan SQLite aislada en memoria o un archivo temporal; no borran ni sustituyen la base de desarrollo.

## Despliegue gratuito en Render y Neon

El blueprint [render.yaml](./render.yaml) configura una API Flask en Render Free. Usa Neon Free para PostgreSQL: la base permanece separada del servicio web, cuyo sistema de archivos local no es persistente. Los planes gratuitos tienen límites y no ofrecen garantías de disponibilidad ni copias de seguridad de nivel producción.

1. Crea un proyecto PostgreSQL en Neon, elige una región cercana a Render y copia su cadena de conexión con SSL. No la publiques ni la agregues a Git.
2. Sube el repositorio a GitHub y, en Render, crea un servicio desde el blueprint seleccionando ese repositorio y la rama `main`.
3. Cuando Render solicite `DATABASE_URL`, pega la cadena de conexión de Neon. Render también generará `SECRET_KEY` y `JWT_SECRET_KEY`; mantenlas como variables privadas.
4. Espera a que termine el despliegue. Prueba `https://<nombre-del-servicio>.onrender.com/`; debe responder con el estado de FINTRACK. La migración de la base se ejecuta al iniciar.
5. En Android, configura `https://<nombre-del-servicio>.onrender.com/api` como servidor. El servicio gratuito puede tardar en responder al primer pedido después de estar inactivo.

No uses la base SQLite local en el servicio de Render ni subas `backend/instance/fintrack.db`: contiene datos locales y no forma parte del despliegue.

## Despliegue público en un VPS

El despliegue de producción usa Docker Compose: Waitress sirve Flask dentro de la red privada de contenedores, Caddy termina TLS/HTTPS y SQLite permanece en un volumen Docker persistente. El puerto interno `8000` no se publica; solo Caddy expone `80` y `443`.

Requisitos: VPS Linux con Docker Engine y plugin Docker Compose, un dominio o subdominio apuntando por DNS a la IP pública del VPS, y los puertos `80/tcp` y `443/tcp` permitidos en el firewall del proveedor.

1. Copia el repositorio al VPS y entra a `deploy`.
2. Copia `.env.example` a `.env`; establece `DOMAIN`, `SECRET_KEY` y `JWT_SECRET_KEY` con valores privados, diferentes y aleatorios de al menos 32 caracteres. La API rechaza las claves de ejemplo y las claves idénticas. Puedes generar cada clave con `python -c "import secrets; print(secrets.token_urlsafe(48))"`.
3. Inicia el servicio con `docker compose up -d --build`.
4. Comprueba el estado con `docker compose ps` y los registros con `docker compose logs -f api caddy`.
5. Configura el APK con `https://<DOMAIN>/api` desde la pantalla de acceso o la opción **Servidor**.

La primera ejecución aplica las migraciones. `fintrack_data` conserva SQLite al recrear contenedores; configura además una copia de seguridad periódica del volumen. Esta configuración es para una sola instancia de la API. No migres la base de desarrollo automáticamente: haz una copia segura y restaúrala explícitamente si necesitas conservar esos datos.

## Clientes

El APK se desarrolla por separado en la carpeta hermana `FINTRACK-ANDROID`. Para desarrollo local, configura la URL de la laptop y puerto `5000` en el build debug. En producción, configura `https://<DOMAIN>/api`; los builds release rechazan HTTP. El backend es la fuente de verdad para autenticación, persistencia, reglas y reportes.