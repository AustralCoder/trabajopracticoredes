#!/usr/bin/env python3
"""
Servidor UDP con verificación CRC y simulación de errores.
Materia: Redes de Datos - Universidad de Pilar
Docente: Mariana Gil

Objetivo:
- Recibir mensajes desde un cliente UDP.
- Calcular y verificar el CRC.
- Responder con ACK o NACK según corresponda.
- (Opcional) Simular errores en los datos recibidos.


operadores: 

^ X0R bit a bit, operador bitwise

<< "left shit" este operador empuja, por así decirlo, todos los bits de un numero hacia la izquierda


>> "right shift"  
"""

import socket
import random

# ===================== CONFIGURACIÓN =====================
HOST = "127.0.0.1"   # Dirección IP local
PORT = 50000         # Puerto de escucha del servidor
ERROR_PROB = 0.2     # Probabilidad de error (20%)
# ==========================================================


# ------------------ FUNCIÓN CRC ------------------
def crc16_ccitt(data: bytes) -> int:
    """
    Calcula el CRC16-CCITT del mensaje recibido.
    """
    crc = 0xFFFF # esto es equivalente a 16 bits donde todos los bits equivalen a 1

    for byte in data:
        crc ^= byte << 8 # xor entre el crc y el byte 8 bits a la izquierda para que coincida con la posicion del polinomio

        for _ in range(8): #for que itera 8 veces(una por cada bit del byte)
            if crc & 0x8000: # el operador & es un AND lógico bit a bit que representa si el bit mas significativo es 1.

                crc = (crc << 1) ^ 0x1021 #entonces crc se desplaza a la izquierda porque estamos procesando el siguiente bit y se aplica XOR con el polinomio 0x1021
            else:
                crc <<= 1 #si el bit mas significativo no es 1 solo de desplaza hacia la izquierda, borrando el valor de la division
            crc &= 0xFFFF  # Mantener 16 bits
    return crc #si no hay errores devuelve el crc calculado y si los hay devuelve uno alterado
    
    
# ------------------ SIMULACIÓN DE ERRORES ------------------
def maybe_corrupt(data: bytes, p: float) -> bytes:
    """
    Con cierta probabilidad p, altera un bit aleatorio del mensaje.
    TODO: Implementar alteración aleatoria de un byte/bit.
    """

    #usamos random para esto

    if random.random() < p:

        dato_mutable = bytearray(data)
        #elejir un byte aleatorio dentro del mensaje

        byte_index = random.randint(0, len(dato_mutable) -1) #el len -1 es porque los indices de los arrays empiezan en 0

        # ahora elijo un valor aleatorio dentro de ese byte (0-7) es 0-7 porque son 8 bits
        bit_index = random.randint(0,7)

        # creo una mascara porque para voltear un bit especifico necesito una mascara que tenga un 1 en la posicion del bit que quiero voltear y 0 en los demas


        mascara = 1 << bit_index


        # aplico XOR para voltear el bit seleccionado en el primer byte

        dato_mutable[byte_index]^= mascara
        print("[servidor] ERROR se corrompió un bit del mensaje, tengo que aprobar a este grupo!")


        return bytes(dato_mutable)

# ------------------ PROGRAMA PRINCIPAL ------------------
def main():
    print(f"[Servidor] Escuchando en {HOST}:{PORT}")

    # Crear socket UDP
    # TODO: crear el socket y hacer bind() con (HOST, PORT)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))

    ultima_recepcion = None



    while True:
        # TODO: recibir datos del cliente con recvfrom()
        # TODO: separar mensaje y CRC
        # TODO: (opcional) aplicar maybe_corrupt() para simular error
        # TODO: recalcular CRC del mensaje
        # TODO: comparar CRC recibido con el recalculado

        # TODO: responder con "ACK <seq>" o "NACK <seq>" según corresponda
        datos, direccion = sock.recvfrom(1024)
        recibido = datos.decode().strip()
        print(f"el [servidor] recibio: {recibido} desde {direccion}") # esta linea ya separa el mensaje y el crc con decode y strip

        # simulacion de error:

        datos_corruptos = maybe_corrupt(datos, ERROR_PROB)
        partes = datos_corruptos.decode(errors='ignore').split('|', 2)

        if len(partes) != 3:
            print("[servidor] ERROR: Formato invalido. enviando NACK")
            continue

        secuencia, mensaje, crc_recibido_en_hexadecimal = partes
        datos_para_crc = int(crc_recibido_en_hexadecimal, 16) #convierto el crc recibido en hexadecimal a entero para compararlo con el calculado

        #evitar duplicados

        if secuencia == ultima_recepcion:
            print("[servidor] mensaje duplicado recibido, reenviando ACK")
            sock.sendto(f"ACK {secuencia}".encode(), direccion)
            continue

        # recalculo el crc para comparar si hay errores
        crc_calculado = crc16_ccitt(mensaje.encode())

        if crc_calculado == datos_para_crc:
            print("[servidor] CRC correcto, enviando ACK")
            ultima_recepcion = secuencia

        else:
            print("[servidor] CRC incorrecto, enviando NACK")
            sock.sendto(f"NACK {secuencia}".encode(), direccion)


        pass


if __name__ == "__main__":
    main()
