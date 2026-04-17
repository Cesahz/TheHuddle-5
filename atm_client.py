import sys
import os
import time
import random
import requests
from datetime import datetime, timezone, timedelta

# Permite importar los módulos de la carpeta services
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tokens import TOKENS_VALIDOS
from scenarios import ESCENARIOS

class SimuladorATM:
    def __init__(self, host="http://localhost:5000"):
        self.url = f"{host}/logs"
        self.tokens = {nombre: token for token, nombre in TOKENS_VALIDOS.items()}
        # Distribución para el bot: más retiros exitosos (1) y consultas (7)
        self.pesos_bot = [1, 1, 1, 7, 7, 2, 3, 4, 5, 6] 

    def _enviar(self, logs, token):
        """Método privado y centralizado para disparar HTTP requests."""
        try:
            # Agregamos timeout=5 (espera máximo 5 segundos antes de abortar)
            res = requests.post(
                self.url, 
                json=logs, 
                headers={"Authorization": f"Token {token}"},
                timeout=5
            )
            return res.status_code, res.json()
            
        except requests.exceptions.ConnectionError:
            return None, {"error": "Servidor apagado o inaccesible."}
        except requests.exceptions.Timeout:
            # Capturamos el error si el tiempo se agota
            return None, {"error": "El servidor tardó demasiado en responder (Timeout)."}

    def disparar_escenario(self, numero, silencioso=False):
        """Construye el log, maneja el token y ejecuta el envío."""
        nombre, funcion = ESCENARIOS[numero]
        datos = funcion()
        
        # El escenario 6 es un ataque con token falso
        if numero == 6:
            token, logs = datos["token_falso"], datos["logs"]
        else:
            logs = datos
            token = self.tokens.get(logs[0]["service"])

        # Si estamos en presentación manual, imprimimos el detalle
        if not silencioso:
            print(f"\n[>] Ejecutando: {nombre}")
            for log in logs:
                print(f"    [{log['severity']}] {log['service']} → {log['message']}")

        codigo, respuesta = self._enviar(logs, token)

        # Formateo de la respuesta en una sola línea limpia
        hora = time.strftime("%H:%M:%S")
        if codigo == 201:
            exitosos = sum(1 for r in respuesta.get("resultados", []) if r.get("ok"))
            msg = f"OK → {exitosos}/{len(logs)} logs guardados."
        elif codigo == 401:
            msg = f"Rechazado → {respuesta.get('error')}"
        elif codigo is None:
            msg = f"Fallo → {respuesta['error']}"
        else:
            msg = f"Error HTTP {codigo} → {respuesta}"

        print(f"[{hora}] {nombre.ljust(22)} | {msg}")

    def modo_bot(self, intervalo=1.0):
        """Ataque automatizado continuo para pruebas de estrés."""
        print(f"\n[⚡] Bot iniciado. Disparando cada {intervalo}s. Ctrl+C para detener.\n")
        try:
            while True:
                escenario = random.choice(self.pesos_bot)
                self.disparar_escenario(escenario, silencioso=True)
                time.sleep(intervalo)
        except KeyboardInterrupt:
            print("\n[!] Operación de bot detenida.")
            
    def purgar_logs_manual(self):
        """Calcula el tiempo y ejecuta el DELETE manualmente."""
        print("\n[🧹] Operación de purga iniciada")
        try:
            segundos = int(input("    ¿Borrar logs más viejos de cuántos segundos? (ej. 60): "))
        except ValueError:
            print("    [!] Valor inválido. Cancelando limpieza.")
            return

        limite = datetime.now(timezone.utc) - timedelta(seconds=segundos)
        
        try:
            # Usamos cualquier token válido para la operación de mantenimiento
            token_admin = self.tokens["atm-hardware-service"]
            res = requests.delete(
                f"{self.url}?before={limite.isoformat()}", 
                headers={"Authorization": f"Token {token_admin}"}
            )
            
            if res.status_code == 200:
                eliminados = res.json().get("eliminados", 0)
                print(f"    [OK] Base de datos limpia. Se eliminaron {eliminados} logs.")
            else:
                print(f"    [X] Error del servidor: {res.status_code}")
        except requests.exceptions.ConnectionError:
            print("    [X] Error: Servidor inaccesible.")

    def modo_interactivo(self):
        """Panel manual para presentar ante evaluadores."""
        print("\n" + "="*45 + "\n PENGUIN LOGGER — Modo Presentación ATM\n" + "="*45)
        while True:
            for num, (nombre, _) in ESCENARIOS.items():
                print(f" [{num}] {nombre}")
            # Añadimos la opción de limpieza visualmente separada
            print(" [8] 🧹 Purgar Base de Datos (DELETE)")
            print(" [0] Salir\n" + "-"*45)
            
            try:
                opcion = int(input("Selecciona una opción: "))
                if opcion == 0: break
                elif opcion == 8: self.purgar_logs_manual()
                elif opcion in ESCENARIOS: self.disparar_escenario(opcion)
                else: print("Opción inválida.")
            except ValueError:
                print("Por favor, ingresa un número.")

if __name__ == "__main__":
    simulador = SimuladorATM()
    
    print("1. Panel Interactivo (Presentación manual)")
    print("2. Bot de Estrés (Generación de tráfico automático)")
    
    eleccion = input("\nElige cómo arrancar (1 o 2): ")
    if eleccion == "1":
        simulador.modo_interactivo()
    elif eleccion == "2":
        simulador.modo_bot(intervalo=1.5)