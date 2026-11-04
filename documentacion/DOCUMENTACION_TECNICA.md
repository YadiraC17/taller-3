# FINTRACK: documento técnico

## Problema y usuario

FINTRACK ayuda a personas que desean registrar ingresos y gastos personales sin mezclar soles peruanos y dólares estadounidenses. El usuario puede organizar sus movimientos, definir límites mensuales y revisar totales calculados con sus datos persistidos.

## Arquitectura

La solución se compone de un frontend HTML/CSS/JavaScript que usa Fetch API, una API REST Flask, servicios para reglas de negocio, repositorios SQLAlchemy y una base SQLite local. Los recursos privados requieren JWT; el backend toma la identidad del token y filtra todas las operaciones por usuario.

## Modelo de datos

El modelo incluye `Usuario`, `Categoria`, `Transaccion` y `Presupuesto`. Un usuario posee categorías, movimientos y presupuestos; una categoría clasifica movimientos y es asociada a límites mensuales. Las claves foráneas de SQLite están activas y las restricciones únicas previenen correos, categorías y presupuestos duplicados.

## Endpoints implementados

La API incluye registro, login y perfil; operaciones CRUD de categorías, transacciones y presupuestos; seguimiento de consumo por presupuesto; y reportes de resumen mensual, distribución por categoría y evolución anual. Los reportes presentan PEN y USD de forma independiente.

## Reglas de negocio

Los montos deben ser positivos y se almacenan con precisión decimal. La categoría debe ser del mismo usuario y coincidir con el tipo de la transacción; los presupuestos aceptan solo categorías de gasto. Una categoría con movimientos o presupuestos no se elimina. El seguimiento compara gasto persistido contra límite y clasifica el consumo en menor a 80%, cerca del límite (80% a menos de 100%) o excedido (100% o más).

## Pruebas y ejecución

La suite automatizada cubre registro/login, correo duplicado, rutas protegidas, validación de montos, aislamiento entre usuarios, conflictos de presupuestos, bloqueo de eliminación relacionada y cálculo de reportes/seguimiento. Se ejecuta con `python -m pytest -q` desde `backend`; las pruebas usan SQLite en memoria. Para la instalación y ejecución reproducibles, seguir el [README](../README.md).