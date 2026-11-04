# Control de cumplimiento FINTRACK

Auditoría del repositorio y de las verificaciones ejecutadas el 03/11/2026. Estados: **Verificado** significa que existe implementación y una comprobación reproducible; **Pendiente** indica que requiere evidencia externa o una acción durante la presentación.

## Entregables

| Requisito | Estado | Evidencia |
|---|---|---|
| Repositorio GitHub con backend, frontend, requisitos, modelos, migraciones y commits | Verificado | Rama `main`, commit `b3ea816` y remoto `origin`. |
| Secretos y entorno local fuera del repositorio | Verificado | `.gitignore`; `.env`, `backend/instance/fintrack.db` y `.venv` ignorados. |
| Documentación de todos los endpoints, métodos, parámetros, autenticación, ejemplos y errores | Verificado | [API.md](API.md). |
| Colección Postman y pasos de importación/ejecución | Verificado | [FINTRACK.postman_collection.json](FINTRACK.postman_collection.json) y API.md. JSON validado. |
| PDF técnico de hasta cinco páginas interiores más carátula | Verificado | [DOCUMENTACION_TECNICA.pdf](DOCUMENTACION_TECNICA.pdf): 2 páginas interiores y carátula. Generable con `generar_pdf.py`. |
| Demostración completa con solicitudes, respuestas y persistencia | Parcial | Flujo completo probado en navegador con SQLite real y revisado en la interfaz; no se archivaron capturas ni grabación en el repositorio. Capturarlas durante la presentación. |

## Requisitos técnicos

| Requisito | Estado | Comprobación |
|---|---|---|
| API REST propia, mínimo cinco endpoints | Verificado | 23 rutas registradas bajo `/api`. |
| Base relacional con al menos dos entidades | Verificado | Cuatro modelos y migración inicial. |
| Operaciones CRUD | Verificado | CRUD de categorías, transacciones y presupuestos; tests HTTP. |
| Lógica de negocio fuera del CRUD | Verificado | Seguimiento presupuestario en servicio; prueba de 425/500 = 85%. |
| Frontend consume cinco o más endpoints | Verificado | Auth, categorías, transacciones, seguimiento y reportes vía Fetch API. Flujo real probado en navegador. |
| Validaciones y códigos HTTP | Verificado | Montos, monedas, tipos, fechas, duplicados y códigos cubiertos por pruebas. |
| Manejo de errores | Verificado | Errores de conexión/respuesta en cliente; 400, 401, 404, 409 y 500 JSON en API. |
| Pruebas automáticas de éxito y fallo | Verificado | 17 pruebas aprobadas; `pytest` usa SQLite en memoria o archivo temporal aislado. |
| Separación rutas, servicios, repositorios y modelos | Verificado | Módulos separados bajo `backend/app/`. |

## Funcionalidad verificada

- Autenticación: registro, login, hashing, token requerido, inválido y expirado; cada cuenta queda aislada.
- Categorías: alta, consulta, edición, eliminación condicionada, duplicados y propiedad.
- Transacciones: alta, consulta, edición, eliminación y filtros de fecha/tipo/categoría/moneda; monto, moneda y tipo validados.
- Presupuestos: CRUD, categoría de gasto, unicidad y seguimiento dentro/cerca/excedido, saldo incluido.
- Reportes: resumen, gastos por categoría y evolución mensual; agregaciones PEN/USD independientes con datos almacenados.
- Persistencia: una prueba escribe en un archivo SQLite y recupera al crear una segunda instancia Flask.
- Interfaz: autenticación, formularios, tablas, filtros, actualización tras guardar y visualizaciones; flujo completo probado en navegador.

## Pendiente antes de presentar

1. Importar la colección Postman, autenticar una cuenta de demostración y mostrar requests/responses.
2. Capturar imágenes de navegador y Postman; guardarlas como evidencia si el curso las solicita.
3. Para demostrar persistencia durante la exposición, crear una transacción, consultar SQLite y reiniciar el backend antes de volver a consultarla.
4. Ejecutar el checklist de nuevo tras cualquier cambio y actualizar este documento y el PDF con los nuevos resultados.

## Comando de verificación

Desde `backend`:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```