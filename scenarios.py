from datetime import datetime, timezone

def marca_de_tiempo():
    """retorna el timestamp actual en formato iso"""
    return datetime.now(timezone.utc).isoformat()


#escenario 1, retiro exitoso
def retiro_exitoso():
    """
    flujo completo de un retiro de 200.000 gs sin errores.
    involucra los 4 servicios en cadena.
    """
    return [
        {
            "timestamp": marca_de_tiempo(),
            "service":   "atm-hardware-service",
            "severity":  "DEBUG",
            "message":   "Tarjeta insertada: VISA **** 4521, chip OK"
        },
        {
            "timestamp": marca_de_tiempo(),
            "service":   "atm-auth-service",
            "severity":  "INFO",
            "message":   "PIN correcto. Sesion iniciada para usuario #3821"
        },
        {
            "timestamp": marca_de_tiempo(),
            "service":   "atm-account-service",
            "severity":  "INFO",
            "message":   "Saldo 1.450.000 Gs. Retiro de 200.000 Gs aprobado"
        },
        {
            "timestamp": marca_de_tiempo(),
            "service":   "atm-cash-service",
            "severity":  "INFO",
            "message":   "Dispensando 200.000 Gs: 2x100.000 Gs. Cassette 1 OK"
        }
    ]


#escenario 2, pin incorrecto
def pin_incorrecto():
    """
    el usuario ingresa un pin erroneo. la auth frena el flujo.
    """
    return [
        {
            "timestamp": marca_de_tiempo(),
            "service":   "atm-hardware-service",
            "severity":  "DEBUG",
            "message":   "Tarjeta insertada: MASTERCARD **** 9032, chip OK"
        },
        {
            "timestamp": marca_de_tiempo(),
            "service":   "atm-auth-service",
            "severity":  "ERROR",
            "message":   "PIN incorrecto. Tarjeta bloqueada tras 3 intentos fallidos"
        }
    ]


#escenario 3 fondos insuficientes
def fondos_insuficientes():
    """
    el usuario tiene saldo pero no alcanza para el retiro solicitado.
    """
    return [
        {
            "timestamp": marca_de_tiempo(),
            "service":   "atm-auth-service",
            "severity":  "INFO",
            "message":   "PIN correcto. Sesion iniciada para usuario #1042"
        },
        {
            "timestamp": marca_de_tiempo(),
            "service":   "atm-account-service",
            "severity":  "WARN",
            "message":   "Saldo insuficiente: 80.000 Gs disponibles, retiro solicitado 200.000 Gs"
        },
        {
            "timestamp": marca_de_tiempo(),
            "service":   "atm-cash-service",
            "severity":  "ERROR",
            "message":   "Retiro rechazado: fondos insuficientes para usuario #1042"
        }
    ]


#escenario 4 cajero sin conexion
def cajero_sin_conexion():
    """
    el hardware detecta que no hay conexion con el servidor central.
    """
    return [
        {
            "timestamp": marca_de_tiempo(),
            "service":   "atm-hardware-service",
            "severity":  "FATAL",
            "message":   "Perdida de conexion con servidor central. ATM fuera de servicio"
        }
    ]


#escenario 5, atasco mecanico
def atasco_mecanico():
    """
    todo va bien hasta que el dispensador de billetes se traba.
    """
    return [
        {
            "timestamp": marca_de_tiempo(),
            "service":   "atm-auth-service",
            "severity":  "INFO",
            "message":   "PIN correcto. Sesion iniciada para usuario #5577"
        },
        {
            "timestamp": marca_de_tiempo(),
            "service":   "atm-cash-service",
            "severity":  "INFO",
            "message":   "Retiro de 500.000 Gs aprobado. Iniciando dispensado"
        },
        {
            "timestamp": marca_de_tiempo(),
            "service":   "atm-cash-service",
            "severity":  "FATAL",
            "message":   "Atasco mecanico en dispensador. Billete trabado en cassette 2"
        }
    ]


#escenario 6, token invalido
def token_invalido():
    """
    simula un servicio que intenta enviar logs con un token falso.
    este escenario no genera logs en la db, solo un 401.
    """
    return {
        "token_falso": "TOKEN-INTRUSO-999",
        "logs": [
            {
                "timestamp": marca_de_tiempo(),
                "service":   "servicio-desconocido",
                "severity":  "INFO",
                "message":   "Intento de acceso no autorizado"
            }
        ]
    }


#escenario 7, consulta de saldo
def consulta_saldo():
    """
    el usuario solo consulta su saldo, sin hacer retiro.
    """
    return [
        {
            "timestamp": marca_de_tiempo(),
            "service":   "atm-auth-service",
            "severity":  "INFO",
            "message":   "PIN correcto. Sesion iniciada para usuario #2290"
        },
        {
            "timestamp": marca_de_tiempo(),
            "service":   "atm-account-service",
            "severity":  "INFO",
            "message":   "Consulta de saldo exitosa: 3.200.000 Gs disponibles"
        }
    ]


#mapa de escenarios
#usado para acceder mucho mas rapido con id
ESCENARIOS = {
    1: ("Retiro exitoso 200.000 Gs", retiro_exitoso),
    2: ("PIN incorrecto",            pin_incorrecto),
    3: ("Fondos insuficientes",      fondos_insuficientes),
    4: ("Cajero sin conexion",       cajero_sin_conexion),
    5: ("Atasco mecanico",           atasco_mecanico),
    6: ("Token invalido",            token_invalido),
    7: ("Consulta de saldo",         consulta_saldo),
}