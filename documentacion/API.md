# Documentación de la API REST FINTRACK

API Flask para autenticación, categorías, transacciones, presupuestos y reportes. La lógica y persistencia se ejecutan en el backend.

## URL base

- **Producción:** `https://fintrack-api-392k.onrender.com/api`
- **Desarrollo local:** `http://127.0.0.1:5000/api` (solo desde la laptop). Para un teléfono en la misma red, usa `http://<IP-DE-LA-LAPTOP>:5000/api`; el build Android debug permite HTTP.
- **Estado del servidor:** `GET https://fintrack-api-392k.onrender.com/` (no lleva `/api`).

La URL de producción gratuita puede tardar en responder cuando Render reactiva el servicio después de un periodo inactivo.

## Formato y autenticación

Las solicitudes con cuerpo deben enviar `Content-Type: application/json`. Los endpoints protegidos requieren:

```http
Authorization: Bearer <access_token>
```

El token se obtiene en `POST /auth/login`, dura 12 horas y se revoca al usar `POST /auth/logout`.

Las respuestas JSON correctas usan este sobre:

```json
{
  "success": true,
  "message": "Operación completada",
  "data": {}
}
```

El listado paginado de transacciones incluye además `pagination`. Las respuestas `204 No Content` de eliminación no tienen cuerpo.

## Rutas

Excepto `GET /`, que consulta la raíz del host, todas las rutas de la tabla son relativas a la URL base `/api`.

| Método | Ruta | Auth | Parámetros / cuerpo | Éxito | Errores esperables |
|---|---|---:|---|---:|---|
| `GET` | `/` (raíz del servidor) | No | Ninguno | `200` | `500` |
| `POST` | `/auth/register` | No | `nombre`, `correo`, `password` | `201` | `400`, `409` |
| `POST` | `/auth/login` | No | `correo`, `password` | `200` | `400`, `401` |
| `GET` | `/auth/me` | Sí | Ninguno | `200` | `401`, `404` |
| `POST` | `/auth/logout` | Sí | Ninguno | `200` | `401` |
| `POST` | `/categorias` | Sí | `nombre`, `tipo`; `descripcion` opcional | `201` | `400`, `401`, `409` |
| `GET` | `/categorias` | Sí | Query opcional `tipo` | `200` | `400`, `401` |
| `GET` | `/categorias/{id_categoria}` | Sí | ID de ruta | `200` | `401`, `404` |
| `PUT` | `/categorias/{id_categoria}` | Sí | `nombre`, `tipo`; `descripcion` opcional | `200` | `400`, `401`, `404`, `409` |
| `DELETE` | `/categorias/{id_categoria}` | Sí | ID de ruta | `204` | `401`, `404`, `409` |
| `POST` | `/transacciones` | Sí | `id_categoria`, `tipo`, `monto`, `moneda`, `fecha`; `descripcion` opcional | `201` | `400`, `401`, `404`, `409` |
| `GET` | `/transacciones` | Sí | Filtros y paginación en query | `200` | `400`, `401` |
| `GET` | `/transacciones/{id_transaccion}` | Sí | ID de ruta | `200` | `401`, `404` |
| `PUT` | `/transacciones/{id_transaccion}` | Sí | Campos de transacción; se pueden omitir campos sin cambios | `200` | `400`, `401`, `404`, `409` |
| `DELETE` | `/transacciones/{id_transaccion}` | Sí | ID de ruta | `204` | `401`, `404` |
| `POST` | `/presupuestos` | Sí | `id_categoria`, `monto_limite`, `moneda`, `mes`, `anio` | `201` | `400`, `401`, `404`, `409` |
| `GET` | `/presupuestos` | Sí | Query opcional `mes`, `anio` | `200` | `400`, `401` |
| `GET` | `/presupuestos/seguimiento` | Sí | Query opcional `mes`, `anio` | `200` | `400`, `401` |
| `GET` | `/presupuestos/{id_presupuesto}` | Sí | ID de ruta | `200` | `401`, `404` |
| `PUT` | `/presupuestos/{id_presupuesto}` | Sí | Campos de presupuesto; se pueden omitir campos sin cambios | `200` | `400`, `401`, `404`, `409` |
| `DELETE` | `/presupuestos/{id_presupuesto}` | Sí | ID de ruta | `204` | `401`, `404` |
| `GET` | `/reportes/resumen` | Sí | Query opcional `mes`, `anio` | `200` | `400`, `401` |
| `GET` | `/reportes/gastos-categoria` | Sí | Query opcional `mes`, `anio` | `200` | `400`, `401` |
| `GET` | `/reportes/evolucion` | Sí | Query opcional `anio` | `200` | `400`, `401` |

Todas las rutas pueden devolver `500` ante un error interno no esperado. Una ruta inexistente devuelve `404`.

### Parámetros y validaciones

- `nombre`: texto obligatorio, máximo 100 caracteres para usuario y 80 para categoría.
- `correo`: correo válido, máximo 150 caracteres; se guarda en minúsculas.
- `password`: mínimo 8 caracteres. Nunca se devuelve en las respuestas.
- `tipo`: `INGRESO` o `GASTO` (no distingue mayúsculas/minúsculas).
- `moneda`: `PEN` o `USD` (no distingue mayúsculas/minúsculas).
- `monto` y `monto_limite`: números mayores que cero, máximo dos decimales.
- `fecha`: formato `YYYY-MM-DD`.
- `mes`: entero de 1 a 12. `anio`: entero de 2000 a 9999, excepto reportes que aceptan hasta 9998.
- `descripcion`: texto opcional de hasta 255 caracteres.
- Una transacción debe usar una categoría del usuario autenticado y el tipo de la transacción debe coincidir con el tipo de la categoría.
- Un presupuesto solo acepta categorías `GASTO`.
- Al actualizar una transacción o presupuesto se pueden enviar solo los campos que cambian. Para categorías `PUT` requiere `nombre` y `tipo`; omitir `descripcion` la deja vacía.

#### Filtros de transacciones

`GET /transacciones` admite:

| Query | Default | Reglas |
|---|---:|---|
| `page` | `1` | Entero mayor o igual a 1 |
| `per_page` | `50` | Entero de 1 a 100 |
| `tipo` | — | `INGRESO` o `GASTO` |
| `moneda` | — | `PEN` o `USD` |
| `categoria` | — | ID entero positivo |
| `fecha_inicio` | — | Fecha ISO inclusiva |
| `fecha_fin` | — | Fecha ISO inclusiva |

Ejemplo: `GET /transacciones?page=1&per_page=50&tipo=GASTO&moneda=PEN&fecha_inicio=2026-01-01&fecha_fin=2026-12-31`.

La respuesta mantiene `data` como arreglo y agrega metadatos:

```json
{
  "success": true,
  "message": "Transacciones consultadas",
  "data": [],
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total": 0,
    "pages": 0,
    "has_next": false,
    "has_prev": false
  }
}
```

Los filtros `mes` y `anio` de presupuestos y reportes aceptan los mismos límites indicados arriba. En reportes, si se omiten, se usa el mes/año actual; la evolución usa el año actual.

## Ejemplos JSON

Los siguientes ejemplos usan `{{baseUrl}}` para la URL base y `{{token}}` para el JWT.

### Registrar una cuenta

`POST {{baseUrl}}/auth/register`

```json
{
  "nombre": "Ana Demo",
  "correo": "ana@example.com",
  "password": "ClaveSegura123"
}
```

Respuesta `201`:

```json
{
  "success": true,
  "message": "Cuenta creada correctamente",
  "data": {
    "usuario": {
      "id_usuario": 1,
      "nombre": "Ana Demo",
      "correo": "ana@example.com",
      "fecha_registro": "2026-11-17T20:00:00+00:00"
    }
  }
}
```

### Iniciar sesión

`POST {{baseUrl}}/auth/login`

```json
{
  "correo": "ana@example.com",
  "password": "ClaveSegura123"
}
```

Respuesta `200`:

```json
{
  "success": true,
  "message": "Inicio de sesión correcto",
  "data": {
    "access_token": "<JWT>",
    "usuario": {
      "id_usuario": 1,
      "nombre": "Ana Demo",
      "correo": "ana@example.com",
      "fecha_registro": "2026-11-17T20:00:00+00:00"
    }
  }
}
```

### Crear una categoría

`POST {{baseUrl}}/categorias` con `Authorization: Bearer {{token}}`:

```json
{
  "nombre": "Alimentación",
  "tipo": "GASTO",
  "descripcion": "Compras y comidas"
}
```

Respuesta `201`:

```json
{
  "success": true,
  "message": "Categoría creada correctamente",
  "data": {
    "id_categoria": 1,
    "nombre": "Alimentación",
    "tipo": "GASTO",
    "descripcion": "Compras y comidas"
  }
}
```

### Crear una transacción

`POST {{baseUrl}}/transacciones`:

```json
{
  "id_categoria": 1,
  "tipo": "GASTO",
  "monto": 42.5,
  "moneda": "PEN",
  "fecha": "2026-11-17",
  "descripcion": "Compra semanal"
}
```

### Crear un presupuesto

`POST {{baseUrl}}/presupuestos`:

```json
{
  "id_categoria": 1,
  "monto_limite": 500,
  "moneda": "PEN",
  "mes": 11,
  "anio": 2026
}
```

### Consultar un reporte

`GET {{baseUrl}}/reportes/resumen?mes=11&anio=2026`:

```json
{
  "success": true,
  "message": "Resumen financiero calculado",
  "data": {
    "periodo": {
      "mes": 11,
      "anio": 2026
    },
    "PEN": {
      "ingresos": 1200,
      "gastos": 42.5,
      "balance": 1157.5
    },
    "USD": {
      "ingresos": 0,
      "gastos": 0,
      "balance": 0
    }
  }
}
```

## Códigos HTTP

| Código | Significado |
|---:|---|
| `200` | Consulta, actualización, login o cierre de sesión exitosos |
| `201` | Recurso creado |
| `204` | Recurso eliminado; respuesta sin cuerpo |
| `400` | JSON, parámetro o dato inválido |
| `401` | Credenciales incorrectas o JWT ausente, inválido, vencido o revocado |
| `404` | Ruta, recurso o categoría del usuario no encontrada |
| `409` | Correo/categoría/presupuesto duplicado o conflicto con relaciones existentes |
| `500` | Error interno no esperado |

Ejemplo de error de validación:

```json
{
  "success": false,
  "message": "El monto debe ser mayor que cero y tener hasta dos decimales",
  "errors": {
    "monto": "Valor no válido"
  }
}
```

## Postman

Importa [`FINTRACK.postman_collection.json`](./FINTRACK.postman_collection.json). La colección define `baseUrl`, `serverUrl` y `token`, y guarda automáticamente el JWT después de un login exitoso. Cambia `correo` por una dirección nueva si vuelves a ejecutar el registro. Las solicitudes de limpieza y cierre de sesión están al final. Para una base local, cambia las variables de URL en Postman. No exportes ni compartas una colección que contenga tu token real.
