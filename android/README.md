# FINTRACK Android

Cliente Android nativo para la API REST de FINTRACK. Android envía solicitudes HTTPS al servidor, presenta resultados y conserva el JWT de sesión. Los cálculos de resumen, gastos por categoría, evolución y seguimiento presupuestario los realiza el backend.

Este proyecto Android está incluido en la carpeta `android/` de este repositorio.

## Arquitectura de ejecución

```text
Android (cliente HTTPS/JWT)
        |
        | HTTPS en producción; HTTP solo en debug local
        v
Servidor Flask -> servicios y reportes -> SQLAlchemy -> base de datos
```

El móvil consume, entre otros, estos endpoints protegidos:

- `GET /api/reportes/resumen?mes=<mes>&anio=<anio>`
- `GET /api/reportes/gastos-categoria?mes=<mes>&anio=<anio>`
- `GET /api/reportes/evolucion?anio=<anio>`
- `GET /api/presupuestos/seguimiento?mes=<mes>&anio=<anio>`
- `GET /api/transacciones?page=<pagina>&per_page=50` (máximo 100 por página)
- `POST /api/auth/logout` para revocar el JWT de la sesión actual

Android envía el token con `Authorization: Bearer <JWT>`. No se implementan cálculos de reportes en la app; el servidor obtiene la identidad del token y consulta los datos del usuario en la base de datos configurada.

## Iniciar el servidor en la laptop

1. Conecta laptop y teléfono a la misma red Wi-Fi.
2. En la carpeta `backend` del proyecto FINTRACK, ejecuta:

```powershell
.\.venv\Scripts\flask.exe --app run run --host 0.0.0.0 --port 5000
```

`0.0.0.0` permite conexiones entrantes de la red local; la URL no se usa como dirección del cliente. Mantén activa esta terminal durante el uso de Android.

3. En Windows, permite conexiones TCP entrantes al puerto 5000 para redes privadas cuando el Firewall lo solicite. El build `debug` permite HTTP para esta prueba local. No configures port forwarding ni expongas este servidor de desarrollo directamente a Internet.
4. Obtén la IPv4 Wi-Fi de la laptop con `ipconfig` (sección del adaptador inalámbrico). Por ejemplo, si es `192.168.1.34`, en la pantalla de acceso Android configura:

```text
http://192.168.1.34:5000/api
```

La dirección debe ser la IPv4 actual de la laptop, no `localhost` ni `127.0.0.1` desde el teléfono. La app la guarda para los siguientes inicios y permite cambiarla con **Servidor** si cambia la IP. Para que distintos teléfonos la encuentren de forma estable, configura una reserva DHCP en el router o usa un nombre DNS local. En el emulador Android puede usarse `http://10.0.2.2:5000/api`.

## Compilar

Requisitos: JDK 17 o superior, Android SDK con plataforma 35 y Android Gradle Plugin/Gradle compatibles.

Desde la carpeta del proyecto Android:

```powershell
.\gradlew.bat assembleDebug
```

El APK de depuración se genera en `app/build/outputs/apk/debug/app-debug.apk`. `local.properties` contiene la ruta local del SDK y no se debe compartir. En esta laptop, si Gradle no puede descargar AAPT2 desde Google Maven, puede usarse el AAPT2 del SDK instalado:

```powershell
.\gradlew.bat assembleDebug "-Pandroid.aapt2FromMavenOverride=$env:LOCALAPPDATA/Android/Sdk/build-tools/36.0.0/aapt2.exe"
```

Para una prueba local, instala el APK debug y usa la IP LAN indicada arriba. El APK release incluye la URL HTTPS de producción y no muestra controles de configuración del servidor, por lo que el usuario no tiene que introducirla.

## Seguridad de red

Los builds `release` requieren HTTPS; el permiso HTTP se habilita solo en `debug` para desarrollo local. La URL de producción se define en `DEFAULT_API_BASE` antes de compilar el APK. No publiques el puerto 5000 en Internet: usa HTTPS, secretos propios y un servidor WSGI de producción.