# API REST — iot-webapp

Aplicación Node.js/Express para CRUDL de lecturas IoT almacenadas en MongoDB (colección `esp32_lecturas`).

## Arquitectura

```
┌─────────────────────────────────────────────────┐
│                   iot-webapp                    │
│              (Node.js + Express)                │
│                                                  │
│  ┌──────────┐  ┌──────────────┐  ┌───────────┐ │
│  │ Rutas     │  │ Controlador  │  │ Mongoose  │ │
│  │ Web (EJS) │──│ (negocio)   │──│ (ODM)     │ │
│  └──────────┘  └──────────────┘  └─────┬─────┘ │
│  ┌──────────┐                           │       │
│  │ Rutas    │───────────────────────────┘       │
│  │ API REST │                                   │
│  └──────────┘                                   │
└─────────────────────────────────────────────────┘
                      │
                      ▼
            ┌──────────────────┐
            │    MongoDB       │
            │  iot-mongodb:    │
            │   27017 / iot    │
            └──────────────────┘
```

## Requisitos del JSON (body de entrada/salida)

### Campos obligatorios

| Campo       | Tipo    | Descripción                        |
|-------------|---------|------------------------------------|
| `valor`     | number  | Valor numérico con decimales       |
| `sensor`    | string  | Identificador del sensor           |
| `ubicacion` | string  | Ubicación física del sensor        |
| `fecha_hora`| string  | Fecha y hora en formato ISO8601    |
| `nodered`   | boolean | Indicador de origen NodeRED        |

### Ejemplo de documento válido

```json
{
  "valor": 23.45,
  "sensor": "DHT22_001",
  "ubicacion": "OFICINA 1",
  "fecha_hora": "2026-05-23T12:30:00.000Z",
  "nodered": true,
  "extra": "cualquier campo adicional"
}
```

> El esquema acepta campos adicionales (`strict: false` en Mongoose).

## Endpoints API REST

Base URL: `http://localhost:3000/api/lecturas`

### GET `/api/lecturas` — Listar todos

Devuelve un array JSON con todas las lecturas, ordenadas por `fecha_hora` descendente.

**Query params opcionales:**
| Parámetro  | Ejemplo             | Descripción                          |
|------------|---------------------|--------------------------------------|
| `sensor`   | `?sensor=DHT22_001` | Filtra por sensor                    |
| `ubicacion`| `?ubicacion=OFICINA`| Filtra por ubicación                 |

**Ejemplo:**
```bash
curl http://localhost:3000/api/lecturas?ubicacion=OFICINA%201
```

### GET `/api/lecturas/:id` — Obtener uno

**Ejemplo:**
```bash
curl http://localhost:3000/api/lecturas/664a1b2c3d4e5f6a7b8c9d0e
```

**Respuesta:** Objeto JSON de la lectura o `404 { error: "No encontrado" }`.

### POST `/api/lecturas` — Crear

**Ejemplo:**
```bash
curl -X POST http://localhost:3000/api/lecturas \
  -H "Content-Type: application/json" \
  -d '{
    "valor": 25.8,
    "sensor": "DHT22_002",
    "ubicacion": "SALON",
    "fecha_hora": "2026-05-23T15:00:00.000Z",
    "nodered": false
  }'
```

**Respuesta:** `201` con el objeto creado.

### PUT `/api/lecturas/:id` — Reemplazar

Requiere el body completo con todos los campos obligatorios.

**Ejemplo:**
```bash
curl -X PUT http://localhost:3000/api/lecturas/664a1b2c3d4e5f6a7b8c9d0e \
  -H "Content-Type: application/json" \
  -d '{
    "valor": 30.1,
    "sensor": "DHT22_002",
    "ubicacion": "COCINA",
    "fecha_hora": "2026-05-23T16:00:00.000Z",
    "nodered": true
  }'
```

### DELETE `/api/lecturas/:id` — Eliminar

**Ejemplo:**
```bash
curl -X DELETE http://localhost:3000/api/lecturas/664a1b2c3d4e5f6a7b8c9d0e
```

**Respuesta:** `{ "mensaje": "Eliminado correctamente" }` o `404`.

## Rutas Web (Interfaz Bootstrap)

Base URL: `http://localhost:3000`

| Método | Ruta          | Descripción                          |
|--------|---------------|--------------------------------------|
| GET    | `/`           | Listado de lecturas con tabla        |
| GET    | `/create`     | Formulario para nueva lectura        |
| POST   | `/create`     | Procesa creación y redirige a `/`    |
| GET    | `/edit/:id`   | Formulario de edición                |
| POST   | `/edit/:id`   | Procesa edición y redirige a `/`     |
| POST   | `/delete/:id` | Elimina y redirige a `/`             |

## Códigos de error HTTP

| Código | Significado                  |
|--------|------------------------------|
| 200    | Éxito (GET, PUT)             |
| 201    | Creado (POST)                |
| 404    | Recurso no encontrado        |
| 422    | Error de validación          |
| 500    | Error interno del servidor   |

## Colección MongoDB

- **Base de datos:** `iot`
- **Colección:** `esp32_lecturas`
- **Conexión:** `mongodb://iot-mongodb:27017/iot` (desde la red Docker `iot-net`)
