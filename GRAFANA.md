# Grafana — Visualización y Dashboards

Grafana está disponible en [http://localhost:3000](http://localhost:3000) con credenciales por defecto:

| Campo    | Valor  |
|----------|--------|
| Usuario  | `admin`|
| Password | `admin`|

## Agregar InfluxDB como datasource

1. Ir a **Connections → Data Sources → Add data source**.
2. Buscar **InfluxDB** y seleccionarlo.
3. Configurar:
   - **Name**: `InfluxDB IoT`
   - **URL**: `http://iot-influxdb:8181`
   - **Access**: `Proxy` (recomendado) o `Browser`
   - **Auth**: desactivar _Basic Auth_
4. En **InfluxDB Details**:
   - **Database**: `iot_lecturas`
   - **HTTP Method**: `GET`
5. Hacer clic en **Save & Test**.

## Ejemplo: dashboard de sensores

1. Ir a **Create → Dashboard → Add visualization**.
2. Seleccionar el datasource **InfluxDB IoT**.
3. En la pestaña **Query**, escribir:
   ```sql
   SELECT * FROM "mediciones"
   WHERE ("sensor" = 'DHT22_001')
   AND time >= now() - 1h
   ```
4. Elegir visualización tipo **Table** o **Time series**.
5. Asignar nombre al panel y hacer clic en **Apply**.

## Comandos útiles

```bash
# Ver logs
docker logs -f iot-grafana

# Acceder al shell
docker exec -it iot-grafana /bin/sh
```

## Uso manual con docker run

```bash
# Crear volumen
docker volume create grafana_data

# Iniciar contenedor
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
