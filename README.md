# Simulación IoT — NodeRED + Mosquitto MQTT + MongoDB

Proyecto para simular comunicaciones en Internet of Things (IoT) usando **NodeRED** como orquestador de flujos, **Eclipse Mosquitto** como broker MQTT, **MongoDB** como base de datos, **InfluxDB 3 Core** como base de datos de series de tiempo, **Grafana** para visualización y dashboards, y dos aplicaciones web CRUDL: **iot-webapp** (Node.js/Express, puerto 3001) e **iot-fastapi** (Python/FastAPI, puerto 5000).

## Arquitectura

```
                                             ┌──────────────────┐
                                             │     Grafana      │
                                             │   (3000 web)     │
                                             └────────┬─────────┘
                                                      │ queries
                       ┌──────────────────┐  ┌────────▼─────────┐
                       │  iot-webapp      │  │  iot-influxdb    │
                       │ (3001 API + Web)  │  │  (8181 API TSDB)│
                       └────────┬─────────┘  └──────────────────┘
                                │ reads/writes
                       ┌────────▼───────────────────────┐
                       │            MongoDB             │
                       │           (27017)              │
                       └────────────────▲───────────────┘
                                         │ writes
                            ┌────────────┴─────────────┐
                            │         NodeRED          │
                            │    (1880 editor + API)   │
                            └─────────────▲────────────┘
                                          │  MQTT pub/sub
                             ┌───────────┴───────────┐
                             │      Mosquitto       │
                             │(1883 MQTT/9001 WS)   │
                             └──────────────────────┘
```

Los contenedores comparten la red `iot-net` y se comunican internamente por el nombre del servicio (`mosquitto`, `nodered`, `mongodb`, `webapp`, `fastapi`, `influxdb`, `grafana`).

## Servicios y puertos expuestos

| Servicio  | Puerto | Protocolo         | Función                                               |
|-----------|--------|-------------------|-------------------------------------------------------|
| NodeRED   | `1880` | HTTP              | Editor, dashboard y endpoints httpIn (todo en un puerto)|
| Mosquitto | `1883` | MQTT (TCP)        | Broker MQTT estándar para pub/sub de dispositivos     |
| Mosquitto | `9001` | MQTT over WebSock | Permite conexión MQTT desde clientes web/navegador    |
| MongoDB   | `27017`| MongoDB wire      | Base de datos NoSQL para persistencia de datos IoT    |
| WebApp    | `3001` | HTTP              | API REST + interfaz web CRUDL (Node.js/Express)      |
| FastAPI   | `5000` | HTTP              | API REST + interfaz web CRUDL (Python/FastAPI)       |
| Grafana   | `3000` | HTTP              | Visualización y dashboards (InfluxDB + MongoDB)      |
| InfluxDB  | `8181` | HTTP API          | Base de datos de series de tiempo (Time Series DB)   |
| InfluxDB UI | `8080` | HTTP            | InfluxDB Explorer UI (oficial)                       |

## Estructura del proyecto

```
.
├── docker-compose.yml         # Orquestación de servicios
├── Dockerfile.nodered         # Imagen personalizada de NodeRED
├── API-REST.md                # Documentación API REST (Node.js)
├── FASTAPI-REST.md            # Documentación API REST (FastAPI)
├── GRAFANA.md                 # Documentación de Grafana
├── INFLUXDB.md                # Documentación de InfluxDB 3 Core
├── webapp/
│   ├── Dockerfile             # Imagen Node.js/Express
│   ├── package.json
│   └── src/                   # Código fuente Node.js
│       ├── index.js
│       ├── config/db.js
│       ├── models/lectura.js
│       ├── controllers/
│       ├── routes/
│       ├── middleware/
│       └── views/
├── fastapi_app/
│   ├── Dockerfile             # Imagen Python/FastAPI
│   ├── requirements.txt
│   └── app/                   # Código fuente Python
│       ├── main.py
│       ├── config/db.py
│       ├── models/lectura.py
│       ├── controllers/
│       ├── routes/
│       └── templates/
├── mosquitto/
│   └── config/
│       └── mosquitto.conf     # Configuración del broker MQTT
└── README.md
```

## Comandos de uso

### Construir y levantar los contenedores

```bash
docker compose up -d --build
```

### Ver logs en vivo

```bash
docker compose logs -f
```

### Detener contenedores

```bash
docker compose down
```

### Detener y eliminar volúmenes (borra datos persistidos)

```bash
docker compose down -v
```

### Reiniciar un servicio específico

```bash
docker compose restart nodered
```

### Acceder al shell de un contenedor

```bash
docker exec -it iot-nodered /bin/bash
docker exec -it iot-mosquitto /bin/sh
docker exec -it iot-webapp /bin/sh
docker exec -it iot-fastapi /bin/sh
docker exec -it iot-grafana /bin/sh
docker exec -it iot-influxdb /bin/sh
```

## Uso sin Docker Compose (solo docker run)

Alternativa usando comandos `docker run` directamente, sin `docker-compose.yml` ni `Dockerfile`. Se usa la imagen base oficial de NodeRED (sin paquetes extra).

```bash
# 1. Crear la red compartida
docker network create iot-net

# 2. Crear volúmenes persistentes
docker volume create mosquitto_data
docker volume create mosquitto_log
docker volume create nodered_data
docker volume create mongodb_data
docker volume create influxdb_data
docker volume create grafana_data


# 3. Iniciar Mosquitto
docker run -d \
  --name iot-mosquitto \
  --restart unless-stopped \
  -p 1883:1883 \
  -p 9001:9001 \
  -v "$(pwd)/mosquitto/config/mosquitto.conf:/mosquitto/config/mosquitto.conf:ro" \
  -v mosquitto_data:/mosquitto/data \
  -v mosquitto_log:/mosquitto/log \
  --network iot-net \
  eclipse-mosquitto:2

# 4. Iniciar MongoDB
docker run -d \
  --name iot-mongodb \
  --restart unless-stopped \
  -p 27017:27017 \
  -v mongodb_data:/data/db \
  --network iot-net \
  mongo:7

# 5. Iniciar NodeRED
docker run -d \
  --name iot-nodered \
  --restart unless-stopped \
  -p 1880:1880 \
  -v nodered_data:/data \
  -e TZ=America/Santiago \
  --sysctl net.ipv6.conf.all.disable_ipv6=1 \
  --network iot-net \
  nodered/node-red:4.0.2

# 6. Iniciar WebApp
docker run -d \
  --name iot-webapp \
  --restart unless-stopped \
  -p 3001:3001 \
  -e MONGODB_URI=mongodb://iot-mongodb:27017/iot \
  -e PORT=3001 \
  --network iot-net \
  opencode_iot-webapp

# 7. Iniciar FastAPI
docker build -t opencode_iot-fastapi ./fastapi_app
docker run -d \
  --name iot-fastapi \
  --restart unless-stopped \
  -p 5000:5000 \
  -e MONGODB_URI=mongodb://iot-mongodb:27017/iot \
  --network iot-net \
  opencode_iot-fastapi

# 8. Iniciar InfluxDB 3 Core
docker run -d \
  --name iot-influxdb \
  --restart unless-stopped \
  -p 8181:8181 \
  -v influxdb_data:/var/lib/influxdb3 \
  --network iot-net \
  influxdb:3-core \
  serve --node-id iot-node \
  --object-store file \
  --data-dir /var/lib/influxdb3 \
  --http-bind 0.0.0.0:8181

# 9. Iniciar InfluxDB Explorer UI
docker run -d \
  --name iot-influxdb-ui \
  --restart unless-stopped \
  -p 8080:8080 \
  -v influxdb_ui_db:/db \
  -e UI_MODE=admin \
  --network iot-net \
  influxdata/influxdb3-ui:latest

# 10. Iniciar Grafana
docker run -d \
  --name iot-grafana \
  --restart unless-stopped \
  -p 3000:3000 \
  -v grafana_data:/var/lib/grafana \
  -e GF_SECURITY_ADMIN_USER=admin \
  -e GF_SECURITY_ADMIN_PASSWORD=admin \
  --network iot-net \
  grafana/grafana:latest
```
> **Nota:** La webapp requiere build previo con `docker build -t opencode_iot-webapp ./webapp`. Si se usa NodeRED base, los paquetes extra deben instalarse desde Manage Palette. Si se obtiene error `EACCES`:
>
> ```bash
> docker exec -it iot-nodered sh -c "rm -rf /tmp/.npm /root/.npm && npm cache clean --force"
> ```

### Detener y eliminar contenedores

```bash
docker stop iot-nodered iot-mongodb iot-mosquitto iot-webapp iot-fastapi iot-grafana iot-influxdb iot-influxdb-ui
docker rm iot-nodered iot-mongodb iot-mosquitto iot-webapp iot-fastapi iot-grafana iot-influxdb iot-influxdb-ui
```

## Verificar funcionamiento

1. Abrir NodeRED en el navegador: [http://localhost:1880](http://localhost:1880)
2. Suscribirse tópico de prueba con mosquitto_sub desde otro terminal:
   ```bash
   docker exec -it iot-mosquitto mosquitto_sub -t "test/#"
   ```
3. Publicar un mensaje de prueba:
   ```bash
   docker exec -it iot-mosquitto mosquitto_pub -t "test/hello" -m "Hola IoT"
   ```

## Conexión desde NodeRED a Mosquitto

Dentro del editor NodeRED:
1. Arrastrar un nodo **mqtt in** o **mqtt out**
2. Crear un broker nuevo con:
   - **Server**: `mosquitto` (nombre del servicio en la red Docker)
   - **Port**: `1883`

No se requiere autenticación (`allow_anonymous true`).

## Conexión desde NodeRED a MongoDB

Dentro del editor NodeRED:
1. Arrastrar un nodo **mongodb in** o **mongodb out** (ya viene pre-instalado, ver sección de [Personalización](#agregar-más-nodos-a-nodered))
2. Configurar el servidor MongoDB con:
   - **Host**: `mongodb` (nombre del servicio en la red Docker)
   - **Port**: `27017`
   - **Database**: `iot` (o el nombre que se desee)

No se requiere autenticación por defecto.

### Verificar MongoDB desde terminal

```bash
# Acceder al shell de MongoDB
docker exec -it iot-mongodb mongosh

# Listar bases de datos
> show dbs

# Usar la base de datos IoT
> use iot

# Ver colecciones
> show collections
```

## Endpoints HTTP con httpIn y httpResponse

NodeRED permite crear endpoints HTTP personalizados usando los nodos **httpIn** y **httpResponse**. En NodeRED v4 ambos usan el mismo puerto `1880` (editor y endpoints comparten el servidor).

### Ejemplo: endpoint GET /hola

1. Arrastrar un nodo **httpIn** al canvas.
2. Configurarlo con:
   - **Method**: `GET`
   - **URL**: `/hola`
   - **Name**: (opcional)
3. Arrastrar un nodo **httpResponse** y conectarlo a la salida del **httpIn**.
4. Opcionalmente, agregar un nodo **template** entre ambos para personalizar la respuesta:

```json
{ "payload": "Hola desde NodeRED!" }
```

5. Hacer clic en **Deploy**.

Probar desde terminal:

```bash
curl http://localhost:1880/hola
```

### Endpoints existentes en NodeRED

El proyecto ya incluye flows con endpoints HTTP que consultan MongoDB. Algunos ejemplos:

| Endpoint | Descripción |
|----------|-------------|
| `GET /empresa_acme` | Todos los registros de `empresa_acme` |
| `GET /deposito` | Registros de `super_acme` con ubicación "DEPÓSITO" |

## Aplicación Web CRUDL (iot-webapp)

Servicio web Node.js/Express con API REST e interfaz Bootstrap que opera sobre la colección `esp32_lecturas` en MongoDB.

### Acceso

| Interfaz | URL                              |
|----------|----------------------------------|
| Web UI   | [http://localhost:3001](http://localhost:3001) |
| API REST | `http://localhost:3001/api/lecturas`           |

### Esquema del documento

| Campo       | Tipo    | Requerido |
|-------------|---------|-----------|
| `valor`     | number  | Sí        |
| `sensor`    | string  | Sí        |
| `ubicacion` | string  | Sí        |
| `fecha_hora`| datetime| Sí        |
| `nodered`   | boolean | Sí        |

> La API acepta campos adicionales. Ver `API-REST.md` para la documentación completa de endpoints y ejemplos curl.

## Aplicación Web CRUDL (iot-fastapi)

Servicio web Python/FastAPI con API REST e interfaz Bootstrap que opera sobre la misma colección `esp32_lecturas` en MongoDB.

### Acceso

| Interfaz | URL                              |
|----------|----------------------------------|
| Web UI   | [http://localhost:5000](http://localhost:5000) |
| API REST | `http://localhost:5000/api/lecturas`           |
| Swagger  | [http://localhost:5000/docs](http://localhost:5000/docs) |

### Esquema del documento

Idéntico al de `iot-webapp` (colección compartida `esp32_lecturas`). Ver sección anterior.

### Documentación

Ver `FASTAPI-REST.md` para la documentación completa de endpoints, ejemplos curl y rutas web.

## InfluxDB 3 Core — Series de Tiempo

**InfluxDB 3 Core** es la base de datos de series de tiempo del proyecto, accesible en `http://localhost:8181`.

### Configuración inicial (post-startup)

```bash
# 1. Crear token de administración
docker exec -it iot-influxdb influxdb3 create token --node-id iot-node --admin

# La salida incluirá un token. Guardarlo.

# 2. Crear base de datos
docker exec -it iot-influxdb influxdb3 create database \
  --node-id iot-node \
  --database iot_lecturas \
  --token <TOKEN>

# 3. Verificar
curl http://localhost:8181/health
```

> Ver `INFLUXDB.md` para detalles completos de configuración y ejemplos.

## Grafana — Dashboards

**Grafana** está disponible en [http://localhost:3000](http://localhost:3000) con usuario `admin` / `admin`.

### Agregar InfluxDB como datasource

1. Ir a **Connections → Data Sources → Add data source → InfluxDB**.
2. Configurar:
   - **URL**: `http://iot-influxdb:8181`
   - **Database**: `iot_lecturas`
3. Hacer clic en **Save & Test**.

> Ver `GRAFANA.md` para instrucciones detalladas, ejemplos de queries y dashboards.

## Personalización

### Agregar más nodos a NodeRED

#### Con Dockerfile (recomendado)

Editar `Dockerfile.nodered` y agregar los paquetes npm deseados. Es importante limpiar el caché npm después de la instalación para evitar errores de permisos (`EACCES`) al usar Manage Palette dentro del editor:

```dockerfile
USER root
RUN npm install \
  node-red-contrib-<nombre1> \
  node-red-contrib-<nombre2> && \
  npm cache clean --force && \
  rm -rf /root/.npm
USER node-red
```

Luego reconstruir:

```bash
docker compose up -d --build nodered
```

#### Desde Manage Palette (editor web)

Si se usa la imagen base oficial (`nodered/node-red:4.0.2`) sin Dockerfile personalizado, el caché npm puede quedar con archivos root-owned y causar el error:

```
npm error code EACCES
npm error Your cache folder contains root-owned files
```

Para solucionarlo, ejecutar en el contenedor:

```bash
# 1. Limpiar caché root-owned (ejecutar como root)
docker exec -u root iot-nodered sh -c "rm -rf /root/.npm && npm cache clean --force"

# 2. Instalar el paquete como usuario node-red
docker exec iot-nodered sh -c "npm install node-red-contrib-<nombre>"

# 3. Reiniciar NodeRED para que cargue el nuevo nodo
docker exec iot-nodered sh -c "kill -HUP 1"

# Alternativa: todo en un solo comando como root
docker exec -u root iot-nodered sh -c \
  "rm -rf /root/.npm && npm cache clean --force && su node-red -c 'npm install node-red-contrib-<nombre>'"
```

> **Nota:** Este problema no ocurre si se construye con el `Dockerfile.nodered` incluido en el proyecto, ya que limpia el caché durante el build (`rm -rf /root/.npm`).

### Configurar autenticación en Mosquitto

Editar `mosquitto/config/mosquitto.conf` y agregar:

```
password_file /mosquitto/config/passwd
allow_anonymous false
```

Luego crear el archivo de contraseñas:

```bash
docker exec -it iot-mosquitto mosquitto_passwd -c /mosquitto/config/passwd usuario
```
