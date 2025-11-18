import socket
import random
import crcmod

# ===================== CONFIGURACIÓN =====================
HOST = "127.0.0.1"  # Dirección IP local (localhost)
PORT = 50000        # Puerto de escucha del servidor
ERROR_PROB = 0.2  # Probabilidad de error (20%)
# ==========================================================


# ------------------ FUNCIÓN CRC ------------------
# 1. Definir la función CRC específica que queremos usar.
#    'crc-ccitt-false' es el nombre estándar para:
#    - Poly: 0x1021
#    - Init: 0xFFFF
#    - Rev: False
#    - XorOut: 0x0000
#    Esto crea una FUNCIÓN (crc16_func) que podemos llamar.

crc16_func = crcmod.predefined.mkCrcFun('crc-ccitt-false')

def crc16_ccitt(data: bytes) -> int:
    """
    Calcula el CRC16-CCITT usando la biblioteca crcmod.
    Simplemente llama a la función que definimos arriba.
    """
    return crc16_func(data)

# ------------------ SIMULACIÓN DE ERRORES ------------------
def maybe_corrupt(data: bytes, p: float) -> bytes:
    """
    Con probabilidad 'p', altera (o voltea) un bit aleatorio del mensaje
    """
    if random.random() < p:
        print("[Servidor] ¡ADVERTENCIA! Simulando corrupción de datos...")
        data_mutable = bytearray(data)
        byte_index = random.randint(0, len(data_mutable) - 1)
        bit_index = random.randint(0, 7)
        mascara = 1 << bit_index
        data_mutable[byte_index] ^= mascara
        return bytes(data_mutable)

    return data


# ------------------ PROGRAMA PRINCIPAL ------------------
def main():

    print(f"[Servidor] Iniciando servidor en {HOST}:{PORT}")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    print(f"[Servidor] Escuchando...")

    while True:
        print("\n[Servidor] Esperando un nuevo mensaje...")
        
        data, direccion = sock.recvfrom(1024)
        print(f"[Servidor] Mensaje recibido de {direccion}")

        data_a_procesar = maybe_corrupt(data, ERROR_PROB)

        try:
            partes = data_a_procesar.decode().split('|', 2)
            seq_recibido = partes[0]
            mensaje_recibido = partes[1]
            crc_recibido_hex = partes[2]
            
            datos_para_crc = f"{seq_recibido}|{mensaje_recibido}".encode()
            crc_calculado = crc16_ccitt(datos_para_crc)
            
            crc_recibido_int = int(crc_recibido_hex, 16)

            if crc_calculado == crc_recibido_int:
                print(f"[Servidor] CRC OK (Seq: {seq_recibido}). Enviando ACK.")
                respuesta = f"ACK {seq_recibido}"
            else:
                print(f"[Servidor] CRC ERROR (Seq: {seq_recibido}). Enviando NACK.")
                respuesta = f"NACK {seq_recibido}"
            
            sock.sendto(respuesta.encode(), direccion)

        except (IndexError, UnicodeDecodeError, ValueError) as e:
            print(f"[Servidor] ERROR: Paquete ilegible o mal formado. {e}")
            sock.sendto(f"NACK ?".encode(), direccion)


if __name__ == "__main__":
    main()