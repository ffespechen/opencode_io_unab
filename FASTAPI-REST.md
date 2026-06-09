# API REST — iot-fastapi

Aplicación FastAPI (Python) para CRUDL de lecturas IoT almacenadas en MongoDB (colección `esp32_lecturas`).

## Arquitectura

```
┌───────────────────────────────────────────────────┐
│                  iot-fastapi                      │
│              (FastAPI + Python)                   │
│                                                    │
│  ┌──────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │ Rutas    │  │  Controlador │  │   Motor     │ │
│  │ Web      │──│  (negocio)   │──│  (MongoDB   │ │
│  │(Jinja2)  │  └──────────────┘  │   async)    │ │
│  └──────────┘                     └──────┬──────┘ │
│  ┌──────────┐                            │        │
│  │ Rutas    │────────────────────────────┘        │
│  │ API REST │                                     │
│  └──────────┘                                     │
└───────────────────────────────────────────────────┘
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
  "nodered": true
}
```

## Endpoints API REST

Base URL: `http://localhost:5000/api/lecturas`

### GET `/api/lecturas` — Listar todos

**Query params opcionales:**
| Parámetro  | Descripción                          |
|------------|--------------------------------------|
| `sensor`   | Filtra por sensor                    |
| `ubicacion`| Filtra por ubicación                 |

**Ejemplo:**
```bash
curl 'http://localhost:5000/api/lecturas?sensor=DHT22_001'
```

### GET `/api/lecturas/{id}` — Obtener uno

```bash
curl http://localhost:5000/api/lecturas/664a1b2c3d4e5f6a7b8c9d0e
```

### POST `/api/lecturas` — Crear

```bash
curl -X POST http://localhost:5000/api/lecturas \
  -H "Content-Type: application/json" \
  -d '{
    "valor": 25.8,
    "sensor": "DHT22_002",
    "ubicacion": "SALON",
    "fecha_hora": "2026-05-23T15:00:00.000Z",
    "nodered": false
  }'
```

### PUT `/api/lecturas/{id}` — Reemplazar

```bash
curl -X PUT http://localhost:5000/api/lecturas/664a1b2c3d4e5f6a7b8c9d0e \
  -H "Content-Type: application/json" \
  -d '{
    "valor": 30.1,
    "sensor": "DHT22_002",
    "ubicacion": "COCINA",
    "fecha_hora": "2026-05-23T16:00:00.000Z",
    "nodered": true
  }'
```

### DELETE `/api/lecturas/{id}` — Eliminar

```bash
curl -X DELETE http://localhost:5000/api/lecturas/664a1b2c3d4e5f6a7b8c9d0e
```

**Respuesta:** `{"mensaje": "Eliminado correctamente"}`

## Rutas Web (Interfaz Bootstrap)

Base URL: `http://localhost:5000`

| Método | Ruta          | Descripción                          |
|--------|---------------|--------------------------------------|
| GET    | `/`           | Listado de lecturas con tabla        |
| GET    | `/create`     | Formulario para nueva lectura        |
| POST   | `/create`     | Procesa creación y redirige a `/`    |
| GET    | `/edit/{id}`  | Formulario de edición                |
| POST   | `/edit/{id}`  | Procesa edición y redirige a `/`     |
| POST   | `/delete/{id}`| Elimina y redirige a `/`             |

## Documentación interactiva (Swagger)

FastAPI genera documentación OpenAPI automática disponible en:

| Interfaz | URL                                    |
|----------|----------------------------------------|
| Swagger  | [http://localhost:5000/docs](http://localhost:5000/docs) |
| Redoc    | [http://localhost:5000/redoc](http://localhost:5000/redoc) |

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
- **Conexión:** `mongodb://iot-mongodb:27017/iot`
