import socket
import time
import crcmod 

# ===================== CONFIGURACIÓN =====================
SERVER_HOST = "127.0.0.1"  # IP del servidor
SERVER_PORT = 50000        # Puerto del servidor
TIMEOUT_S = 1.0            # Tiempo máximo de espera (1.0 segundos)
MAX_RETRIES = 5            # Cantidad máxima de reintentos
# ==========================================================

# ------------------ FUNCIÓN CRC ------------------
# 1. Definir la función CRC específica que queremos usar.
#    'crc-ccitt-false' es el nombre estándar para:
#    - Poly: 0x1021
#    - Init: 0xFFFF
#    - Rev: False | rev false significa que no se invierten los bits
#    - XorOut: 0x0000
#    Esto crea una FUNCIÓN (crc16_func) que podemos llamar.

crc16_func = crcmod.predefined.mkCrcFun('crc-ccitt-false')

def crc16_ccitt(data: bytes) -> int:
    """
    Calcula el CRC16-CCITT usando la biblioteca crcmod.
    (Debe ser IDÉNTICA a la del servidor)
    """
    # Simplemente llamamos a la función predefinida
    return crc16_func(data)


# ------------------ ENVÍO CON RETRANSMISIÓN ------------------
def send_with_retries(sock: socket.socket, server_addr, seq_num, message):
    """
    Envía un mensaje con número de secuencia 'seq_num' y retransmite
    si no recibe un ACK correcto en el tiempo establecido.
    """

    # 1. Preparar el paquete. aclaremos que el paquete es: <seq>|<mensaje>|<crc>
    seq_str = str(seq_num)
    datos_para_crc = f"{seq_str}|{message}".encode()
    
    # Llama a la función crc16_ccitt
    crc_calculado = crc16_ccitt(datos_para_crc)
    
    crc_hex = f"{crc_calculado:x}"
    paquete_str = f"{seq_str}|{message}|{crc_hex}"
    paquete_bytes = paquete_str.encode()

    # 2. Bucle de reintentos
    for attempt in range(MAX_RETRIES):
        print(f"\n[Cliente] Intento {attempt + 1}/{MAX_RETRIES}: Enviando (Seq: {seq_str})...")
        
        try:
            # 3. Enviar datos
            sock.sendto(paquete_bytes, server_addr)

            # 4. Esperar respuesta (esta línea se bloquea hasta TIMEOUT)
            data, direccion = sock.recvfrom(1024)
            respuesta = data.decode()
            
            print(f"[Cliente] Servidor respondió: '{respuesta}'")

            # 5. Validar respuesta
            if respuesta == f"ACK {seq_str}":
                print("[Cliente] ¡ACK correcto recibido! Envío exitoso.")
                return True # <-- Éxito, salimos de la función
            else:
                print("[Cliente] NACK o ACK incorrecto. Reintentando...")

        except socket.timeout:
            # 6. Capturar el Timeout
            print("[Cliente] TIMEOUT. El servidor no respondió. Reintentando...")
        
    # 7. Si el bucle 'for' termina, significa que agotamos los reintentos
    print(f"[Cliente] ERROR: Fallaron {MAX_RETRIES} intentos. Abortando.")
    return False # <-- Falla


# ------------------ PROGRAMA PRINCIPAL ------------------
def main():

    print(f"[Cliente] Comunicándose con {SERVER_HOST}:{SERVER_PORT}")

    server_addr = (SERVER_HOST, SERVER_PORT)

    # 1. Crear socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # 2. Establecer timeout en el socket

    sock.settimeout(TIMEOUT_S)

    seq = 0  # Número de secuencia inicial (0) esto sirve para alternar entre 0 y 1

    # 3. Bucle principal del cliente
    while True:
        # 4. Pedir mensaje al usuario
        message = input("\nEscriba un mensaje (o presione ENTER para salir): ")
        
        # 5. Si el mensaje está vacío, terminar
        if not message:
            print("[Cliente] Saliendo.")
            break
        
        # 6. Llamar a la función de envío confiable
        success = send_with_retries(sock, server_addr, seq, message)

        # 7. Alternar número de secuencia SI el envío fue exitoso
        if success:
            seq = 1 - seq
        else:
            print("[Cliente] El mensaje no pudo ser entregado.")

    # 8. Cerrar el socket al salir
    sock.close()


if __name__ == "__main__":
    main()