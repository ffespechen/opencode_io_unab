# Simulación IoT — NodeRED + Mosquitto MQTT

Proyecto para simular comunicaciones en Internet of Things (IoT) usando **NodeRED** como orquestador de flujos y **Eclipse Mosquitto** como broker MQTT.

## Arquitectura

```
┌──────────────┐       MQTT        ┌──────────────┐
│   NodeRED    │◄──────────────►   │   Mosquitto  │
│  (1880 web)  │   pub/sub         │  (1883 MQTT)  │
│              │                   │  (9001 WS)    │
└──────────────┘                   └──────────────┘
```

Ambos contenedores comparten la red `iot-net` y se comunican internamente por los nombres de servicio (`mosquitto`, `nodered`).

## Servicios y puertos expuestos

| Servicio  | Puerto | Protocolo         | Función                                               |
|-----------|--------|-------------------|-------------------------------------------------------|
| NodeRED   | `1880` | HTTP              | Editor visual de flujos y dashboard IoT               |
| Mosquitto | `1883` | MQTT (TCP)        | Broker MQTT estándar para pub/sub de dispositivos     |
| Mosquitto | `9001` | MQTT over WebSock | Permite conexión MQTT desde clientes web/navegador    |

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

# 4. Iniciar NodeRED
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

> **Nota:** NodeRED no incluirá `node-red-dashboard` ni otros paquetes extra. Pueden instalarse desde el panel "Manage palette" dentro del editor en `http://localhost:1880`.

### Detener y eliminar contenedores

```bash
docker stop iot-nodered iot-mosquitto
docker rm iot-nodered iot-mosquitto
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

## Personalización

### Agregar más nodos a NodeRED

Editar `Dockerfile.nodered` y agregar los paquetes npm deseados:

```dockerfile
RUN npm install node-red-contrib-<nombre>
```

Luego reconstruir:

```bash
docker compose up -d --build nodered
```

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
