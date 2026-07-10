# InfluxDB 3 Core — Base de Datos de Series de Tiempo

InfluxDB 3 Core es la versión open source de InfluxDB v3, optimizada para almacenar y consultar datos de series de tiempo (time-series).

## Interfaces de acceso

| Interfaz | URL | Puerto | Descripción |
|----------|-----|--------|-------------|
| API REST | `http://localhost:8181` | 8181 | API directa de InfluxDB |
| Admin UI | `http://localhost:8080` | 8080 | InfluxDB Explorer UI (oficial) |

## Configuración inicial

El contenedor se inicia automáticamente con almacenamiento local (`--object-store file`) en el directorio `/var/lib/influxdb3`.

### 1. Crear un token de administración

Una vez que el contenedor esté corriendo:

```bash
# Crear un token de administración
docker exec -it iot-influxdb influxdb3 create token \
  --node-id iot-node \
  --admin

# La salida será similar a:
# Token: in3k_abc123def456...
```

> **Importante:** Guardar el token generado. Se usará para autenticar escrituras y consultas.

### 2. Crear una base de datos

```bash
docker exec -it iot-influxdb influxdb3 create database \
  --node-id iot-node \
  --database iot_lecturas \
  --token <TOKEN_GENERADO>
```

### 3. Usar InfluxDB Explorer UI

La UI oficial de InfluxDB 3 está disponible en [http://localhost:8080](http://localhost:8080).

1. Abrir [http://localhost:8080](http://localhost:8080) en el navegador.
2. En la pantalla de inicio, hacer clic en **Connect to InfluxDB**.
3. Configurar la conexión:
   - **Cluster URL**: `http://iot-influxdb:8181`
   - **Token**: el token generado en el paso 1
4. Explorar las bases de datos, escribir queries SQL y administrar el servidor desde la interfaz.

> La UI corre en modo `admin` (env `UI_MODE=admin`) para permitir todas las operaciones administrativas.

### Escribir datos de prueba

```bash
curl -X POST http://localhost:8181/api/v2/write?bucket=iot_lecturas \
  -H "Authorization: Bearer <TOKEN_GENERADO>" \
  -H "Content-Type: text/plain; charset=utf-8" \
  -d 'mediciones,sensor=DHT22_001,ubicacion=OFICINA valor=25.5,nodered=true'
```

### Consultar datos

```bash
# vía API
curl -X POST http://localhost:8181/api/v2/query?db=iot_lecturas \
  -H "Authorization: Bearer <TOKEN_GENERADO>" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT * FROM mediciones LIMIT 5"}'
```

## Conexión desde NodeRED (opcional)

Dentro del editor NodeRED (`http://localhost:1880`):

1. Arrastrar un nodo **influxdb out** o **influxdb in**.
2. Crear un servidor nuevo con:
   - **Host**: `iot-influxdb`
   - **Port**: `8181`
   - **Database**: `iot_lecturas`
   - **Token**: el token generado arriba

## Conexión desde Grafana

Ver `GRAFANA.md` para instrucciones de configuración del datasource InfluxDB en Grafana.

## Comandos útiles

```bash
# Ver logs
docker logs -f iot-influxdb

# Acceder al shell
docker exec -it iot-influxdb /bin/sh

# Ver estado
docker exec -it iot-influxdb influxdb3 show databases --node-id iot-node
```

## Uso manual con docker run

```bash
# Crear volúmenes
docker volume create influxdb_data

# 1. Iniciar InfluxDB
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

# 2. Iniciar Admin UI
docker run -d \
  --name iot-influxdb-ui \
  --restart unless-stopped \
  -p 8080:8080 \
  -v influxdb_ui_db:/db \
  -e UI_MODE=admin \
  --network iot-net \
  influxdata/influxdb3-ui:latest
```
