import time
import random
import requests
from tokens import TOKENS_VALIDOS
from scenarios import ESCENARIOS


class SimuladorATM:
    def __init__(self, host="http://localhost:5000"):
        self.url = f"{host}/logs"
        #invertir la clave/valor del diccionario original
        self.tokens = {nombre: token for token, nombre in TOKENS_VALIDOS.items()}
        
        #distribucion de escenarios
        self.pesos_bot = [1, 1, 1, 7, 7, 2, 3, 4, 5, 6]

    #metodo privado porque no se manda manualmente, solo se usa dentro de la clase
    def _enviar(self, logs, token):
        """metodo privado para disparar peticiones http."""
        try:
            #armar el canal de comunicacion con el servidor para mandar datos
            res = requests.post(
                self.url,
                json=logs,
                headers={"Authorization": f"Token {token}"},
                timeout=5
            )
            return res.status_code, res.json()
        
        #reportar el error en caso de errores de conexion o timeout
        except requests.exceptions.ConnectionError:
            return None, {"error": "Servidor apagado o inaccesible."}
        except requests.exceptions.Timeout:
            return None, {"error": "El servidor tardo demasiado en responder (timeout)."}

    def disparar_escenario(self, numero, silencioso=False):
        """construir el log, manejar el token y ejecutar el envio."""
        
        #extraer el nombre y la funcion que retorna json por indice de ESCENARIOS :D
        nombre, funcion = ESCENARIOS[numero]
        datos = funcion()
        
        #validar ataque con token falso en el escenario 6
        if numero == 6:
            token, logs = datos["token_falso"], datos["logs"]
        
        #como el 6 es el unico que manda token falso, el resto se va iwal
        else:
            logs = datos
            token = self.tokens.get(logs[0]["service"])

        #imprimir detalle en modo de presentacion manual
        if not silencioso:
            print(f"\n[>] Ejecutando: {nombre}")
            for log in logs:
                print(f"    [{log['severity']}] {log['service']}")
        
        
        #PROBAR ENVIO y almacenar codigho y respuesta
        codigo, respuesta = self._enviar(logs, token)

        #formatear la respuesta en una sola linea limpia
        hora = time.strftime("%H:%M:%S")
        if codigo == 201:
            exitosos = respuesta.get("insertados", 0)
            msg = f"OK → {exitosos}/{len(logs)} logs guardados."
        elif codigo == 401:
            msg = f"Rechazado → {respuesta.get('error')}"
        elif codigo is None:
            msg = f"Fallo → {respuesta['error']}"
        else:
            msg = f"Error HTTP {codigo} → {respuesta}"

        print(f"[{hora}] {nombre} | {msg}")


    #mandar logs automaticamente y aleatorio cada cierto tiempo
    def modo_bot(self, intervalo=1.0):
        """ataque automatizado continuo para pruebas de estres."""
        print(f"\n[>] Bot iniciado. Disparando cada {intervalo}s. Ctrl+C para detener.\n")
        try:
            while True:
                escenario = random.choice(self.pesos_bot)
                self.disparar_escenario(escenario, silencioso=True)
                time.sleep(intervalo)
        except KeyboardInterrupt:
            print("\n[!] Operacion de bot detenida.")

    #mandar logs manualmente
    def modo_interactivo(self):
        """panel manual para mandar el log"""
        print("\n" + "="*45 + "\n PENGUIN LOGGER — Modo Manuel ATM\n" + "="*45)
        while True:
            for num, (nombre, _) in ESCENARIOS.items():
                print(f" [{num}] {nombre}")
            print(" [0] Salir\n" + "-"*45)
            
            try:
                opcion = int(input("Selecciona una opcion: "))
                if opcion == 0:
                    break
                elif opcion in ESCENARIOS: self.disparar_escenario(opcion)
                else: print("Opción inválida.")
            except ValueError:
                print("Por favor, ingresa un numero.")

if __name__ == "__main__":
    simulador = SimuladorATM()
    
    print("1. Panel Interactivo (Presentacion manual)")
    print("2. Bot de Estres (Generacion de trafico automatico)")
    
    eleccion = input("\nElige como arrancar (1 o 2): ")
    if eleccion == "1":
        simulador.modo_interactivo()
    elif eleccion == "2":
        simulador.modo_bot(intervalo=1.5)