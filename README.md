# Penguin Logger

Sistema de logging distribuido basado en un ATM con 4 servicios independientes que envian logs a un servidor central Flask + SQLite.

---

## Setup

### Crear entorno virtual

```bash
python -m venv venv
```

### Activar entorno virtual

```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## Correr el sistema

```bash
# Terminal 1 — servidor central
python server.py

# Terminal 2 — cliente
python atm_cliente.py

```

Dashboard web disponible en: `http://localhost:5000`

---

## Autenticacion

Todos los endpoints requieren el header:

```
Authorization: Token TOKEN-ATM-001
```

### Tokens validos por servicio

| Token                | Servicio             |
| -------------------- | -------------------- |
| `TOKEN-ATM-001`      | atm-cash-service     |
| `TOKEN-AUTH-002`     | atm-auth-service     |
| `TOKEN-PAYMENTS-003` | atm-account-service  |
| `TOKEN-WATCHDOG-004` | atm-hardware-service |
| `TOKEN-ADMIN-005`    | admin                |

Si el token es invalido o no esta presente, el servidor responde:

```json
{ "error": "Quien sos, bro?" }
```

---

## Endpoints

### POST /logs

Recibe uno o varios logs y los persiste en la base de datos.

**Body — un solo log:**

```json
{
  "timestamp": "2026-04-14T10:00:00Z",
  "service": "atm-cash-service",
  "severity": "INFO",
  "message": "Dispensando $200: 2x$100. Cassette 1 OK"
}
```

**Body — lista de de logs:**

```json
[
  {
    "timestamp": "2026-04-14T10:00:00Z",
    "service": "atm-hardware-service",
    "severity": "DEBUG",
    "message": "Tarjeta insertada: VISA **** 4521, chip OK"
  },
  {
    "timestamp": "2026-04-14T10:00:01Z",
    "service": "atm-auth-service",
    "severity": "INFO",
    "message": "PIN correcto. Sesion iniciada para usuario #3821"
  }
]
```

**Campos obligatorios:**

| Campo       | Tipo            | Descripcion                                                               |
| ----------- | --------------- | ------------------------------------------------------------------------- |
| `timestamp` | string ISO 8601 | Fecha y hora del evento declarada por el servicio                         |
| `service`   | string          | Nombre del servicio que genera el log                                     |
| `severity`  | string          | Nivel del log. Valores validos: `INFO`, `DEBUG`, `WARN`, `ERROR`, `FATAL` |
| `message`   | string          | Descripcion del evento                                                    |

**Respuesta exitosa (201):**

```json
{ "status": "ok", "insertados": 2 }
```

---

### GET /logs

Consulta los logs guardados. Acepta filtros opcionales via query params.

**Parametros opcionales:**

| Parametro         | Tipo            | Descripcion                                  | Ejemplo                |
| ----------------- | --------------- | -------------------------------------------- | ---------------------- |
| `service`         | string          | Filtrar por nombre de servicio               | `atm-cash-service`     |
| `severity`        | string          | Filtrar por nivel de severidad               | `ERROR`                |
| `timestamp_start` | string ISO 8601 | Logs con timestamp mayor o igual             | `2026-04-14T00:00:00Z` |
| `timestamp_end`   | string ISO 8601 | Logs con timestamp menor o igual             | `2026-04-14T23:59:59Z` |
| `limit`           | integer         | Cantidad maxima de resultados (default: 100) | `50`                   |

**Ejemplo de uso:**

```
GET /logs?service=atm-cash-service&severity=ERROR&limit=20
```

**Respuesta exitosa (200):**

```json
{
  "total": 1,
  "logs": [
    {
      "id": 1,
      "service": "atm-cash-service",
      "severity": "ERROR",
      "message": "Retiro rechazado: fondos insuficientes",
      "timestamp": "2026-04-14T10:00:00Z",
      "received_at": "2026-04-14T10:00:01.123456+00:00"
    }
  ]
}
```

---

### GET /stats

Retorna metricas agregadas de los logs guardados.

**Sin parametros.**

**Respuesta exitosa (200):**

```json
{
  "por_servicio": {
    "atm-cash-service": 42,
    "atm-auth-service": 38
  },
  "por_severidad": {
    "INFO": 60,
    "ERROR": 12,
    "WARN": 8
  }
}
```

---

## Codigos HTTP

| Codigo | Nombre                | Cuando ocurre                                            |
| ------ | --------------------- | -------------------------------------------------------- |
| `200`  | OK                    | Consulta exitosa (GET, DELETE)                           |
| `201`  | Created               | Recurso creado exitosamente (POST)                       |
| `400`  | Bad Request           | JSON invalido, campos faltantes o severidad no permitida |
| `401`  | Unauthorized          | Token ausente o invalido                                 |
| `404`  | Not Found             | Ruta no existe                                           |
| `405`  | Method Not Allowed    | Metodo HTTP no permitido en esa ruta                     |
| `500`  | Internal Server Error | Error inesperado en el servidor                          |

---
