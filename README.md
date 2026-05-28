# Simulación IoT — NodeRED + Mosquitto MQTT + MongoDB

Proyecto para simular comunicaciones en Internet of Things (IoT) usando **NodeRED** como orquestador de flujos, **Eclipse Mosquitto** como broker MQTT y **MongoDB** como base de datos.

## Arquitectura

```
                      ┌──────────────┐
                      │   MongoDB    │
                      │  (27017)     │
                      └──────▲───────┘
                             │
                     writes  │  reads
                             │
                ┌────────────┴─────────────┐
                │         NodeRED          │
                │    (1880 editor + API)   │
                └─────────────▲────────────┘
                              │  MQTT pub/sub
                   ┌─────────┴───────────┐
                   │     Mosquitto       │
                   │(1883 MQTT/9001 WS)  │
                   └─────────────────────┘
```

Los contenedores comparten la red `iot-net` y se comunican internamente por el nombre del servicio (`mosquitto`, `nodered`, `mongodb`).

## Servicios y puertos expuestos

| Servicio  | Puerto | Protocolo         | Función                                               |
|-----------|--------|-------------------|-------------------------------------------------------|
| NodeRED   | `1880` | HTTP              | Editor, dashboard y endpoints httpIn (todo en un puerto)|
| Mosquitto | `1883` | MQTT (TCP)        | Broker MQTT estándar para pub/sub de dispositivos     |
| Mosquitto | `9001` | MQTT over WebSock | Permite conexión MQTT desde clientes web/navegador    |
| MongoDB   | `27017`| MongoDB wire      | Base de datos NoSQL para persistencia de datos IoT    |

## Estructura del proyecto

```
.
├── docker-compose.yml         # Orquestación de servicios
├── Dockerfile.nodered         # Imagen personalizada de NodeRED
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
```

> **Nota:** NodeRED no incluirá `node-red-dashboard`, `node-red-contrib-mongodb4` ni otros paquetes extra. Pueden instalarse desde el panel "Manage palette" dentro del editor en `http://localhost:1880`. Si se obtiene el error `EACCES` al instalar, ejecutar este comando para limpiar el caché npm root-owned:
>
> ```bash
> docker exec -it iot-nodered sh -c "rm -rf /tmp/.npm /root/.npm && npm cache clean --force"
> ```

### Detener y eliminar contenedores

```bash
docker stop iot-nodered iot-mongodb iot-mosquitto
docker rm iot-nodered iot-mongodb iot-mosquitto
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
