# API REST FINTRACK

Base URL local: `http://127.0.0.1:5000/api`. Todas las respuestas usan JSON, salvo eliminaciones exitosas, que responden `204 No Content`. Las operaciones protegidas requieren `Authorization: Bearer <JWT>`.

Las respuestas exitosas tienen la forma `{"success": true, "message": "...", "data": ...}`. Los errores incluyen `success: false`, `message` y, cuando aplica, un objeto `errors`.

## Ejemplos de solicitud y respuesta

Registro (`POST /auth/register`, sin token):

```json
{
	"nombre": "Usuario Demo",
	"correo": "demo@fintrack.com",
	"password": "ClaveSegura123"
}
```

Respuesta `201 Created`:

```json
{
	"success": true,
	"message": "Cuenta creada correctamente",
	"data": {
		"usuario": {
			"id_usuario": 1,
			"nombre": "Usuario Demo",
			"correo": "demo@fintrack.com",
			"fecha_registro": "2026-11-03T12:00:00+00:00"
		}
	}
}
```

Inicio de sesión (`POST /auth/login`, sin token) recibe `correo` y `password`. La respuesta `200 OK` incluye `data.access_token` y `data.usuario`; envía el token en el encabezado Bearer para las siguientes solicitudes.

Registrar un gasto (`POST /transacciones`, con token):

```json
{
	"id_categoria": 1,
	"tipo": "GASTO",
	"monto": 45.5,
	"moneda": "PEN",
	"descripcion": "Almuerzo",
	"fecha": "2026-11-03"
}
```

Respuesta `201 Created`:

```json
{
	"success": true,
	"message": "Transacción registrada correctamente",
	"data": {
		"id_transaccion": 1,
		"id_categoria": 1,
		"categoria": "Alimentación",
		"tipo": "GASTO",
		"monto": 45.5,
		"moneda": "PEN",
		"descripcion": "Almuerzo",
		"fecha": "2026-11-03"
	}
}
```

Crear un presupuesto (`POST /presupuestos`, con token) recibe `id_categoria`, `monto_limite`, `moneda`, `mes` y `anio`. Por ejemplo: `{"id_categoria": 1, "monto_limite": 500, "moneda": "PEN", "mes": 11, "anio": 2026}`.

Una respuesta de error de validación (`400 Bad Request`) tiene esta forma:

```json
{
	"success": false,
	"message": "El monto debe ser mayor que cero y tener hasta dos decimales",
	"errors": { "monto": "Valor no válido" }
}
```

## Autenticación

| Método | URL | Autenticación | Uso |
|---|---|---|---|
| POST | `/auth/register` | No | Crear usuario con `nombre`, `correo`, `password` (mínimo 8 caracteres). Responde 201. |
| POST | `/auth/login` | No | Recibe `correo` y `password`; devuelve `access_token` y usuario. |
| GET | `/auth/me` | Sí | Devuelve el usuario asociado al token. |
| GET | `/auth/logout` | Sí | Informa que el cliente debe borrar el token; no revoca JWT en servidor. |

## Categorías

Todas las categorías pertenecen al usuario del token. Los tipos permitidos son `INGRESO` y `GASTO`.

| Método | URL | Uso |
|---|---|---|
| POST | `/categorias` | Crear con `nombre`, `tipo` y opcionalmente `descripcion`. Responde 201. |
| GET | `/categorias` | Listar; admite `?tipo=GASTO` o `?tipo=INGRESO`. |
| GET | `/categorias/{id}` | Consultar una categoría propia. |
| PUT | `/categorias/{id}` | Reemplazar `nombre`, `tipo` y `descripcion`. |
| DELETE | `/categorias/{id}` | Eliminar si no tiene transacciones ni presupuestos. |

## Transacciones

Crear y actualizar reciben `id_categoria`, `tipo`, `monto`, `moneda`, `fecha` (`YYYY-MM-DD`) y opcionalmente `descripcion`. La moneda es `PEN` o `USD`, y el monto debe ser positivo con hasta dos decimales.

| Método | URL | Uso |
|---|---|---|
| POST | `/transacciones` | Registrar una transacción. Responde 201. |
| GET | `/transacciones` | Listar; filtros opcionales `tipo`, `moneda`, `categoria`, `fecha_inicio`, `fecha_fin`. |
| GET | `/transacciones/{id}` | Consultar una transacción propia. |
| PUT | `/transacciones/{id}` | Actualizar una transacción propia. |
| DELETE | `/transacciones/{id}` | Eliminar una transacción propia. |

## Presupuestos

Crear/actualizar reciben `id_categoria`, `monto_limite`, `moneda`, `mes` (1-12) y `anio`. La categoría debe ser propia y de tipo `GASTO`.

| Método | URL | Uso |
|---|---|---|
| POST | `/presupuestos` | Crear un presupuesto. Responde 201. |
| GET | `/presupuestos` | Listar; admite filtros opcionales `mes` y `anio`. |
| GET | `/presupuestos/{id}` | Consultar un presupuesto propio. |
| PUT | `/presupuestos/{id}` | Actualizar un presupuesto propio. |
| DELETE | `/presupuestos/{id}` | Eliminar un presupuesto propio. |
| GET | `/presupuestos/seguimiento?mes=11&anio=2026` | Devuelve gasto real, porcentaje, saldo y estado por presupuesto. |

Estados del seguimiento: `DENTRO_DEL_PRESUPUESTO` (<80%), `CERCA_DEL_LIMITE` (80% a <100%) y `EXCEDIDO` (>=100%).

## Reportes

| Método | URL | Uso |
|---|---|---|
| GET | `/reportes/resumen?mes=11&anio=2026` | Ingresos, gastos y balance mensual separados por PEN y USD. |
| GET | `/reportes/gastos-categoria?mes=11&anio=2026` | Distribución de gastos por categoría y moneda. |
| GET | `/reportes/evolucion?anio=2026` | Totales mensuales de ingresos y gastos por moneda. |

Los parámetros de periodo son opcionales en los dos primeros reportes; por defecto se usa el mes actual. La evolución usa el año actual por defecto.

## Códigos de respuesta

`200` operación correcta; `201` creado; `204` eliminado; `400` entrada inválida; `401` token ausente, inválido o expirado; `404` recurso inexistente o ajeno al usuario; `409` duplicidad o conflicto con relaciones existentes; `500` error interno sin detalles técnicos.

## Importar y probar con Postman

1. Inicia el backend siguiendo el README y verifica `http://127.0.0.1:5000/`.
2. En Postman, selecciona **Import**, elige `documentacion/FINTRACK.postman_collection.json` y confirma la colección FINTRACK API.
3. Envía **Registrar usuario** una vez con un correo nuevo. Si el usuario ya existe, omite esa solicitud.
4. Envía **Iniciar sesión**. El script guarda automáticamente `data.access_token` en la variable de colección `token`; no es necesario crear un entorno de Postman.
5. Envía **Crear categoría de gasto** para guardar `categoriaId`; luego ejecuta los requests de transacciones, presupuesto y reportes.
6. La colección usa por defecto el periodo noviembre de 2026; actualiza `mes` y `anio` en los requests para probar otro periodo.

La variable `baseUrl` puede cambiarse en Postman para apuntar a otro entorno. No compartas ni guardes el token de acceso en un repositorio.