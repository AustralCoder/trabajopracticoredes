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
    TODO: Implementar el algoritmo bit a bit o con polinomio 0x1021.
    """
    pass


# ------------------ SIMULACIÓN DE ERRORES ------------------
def maybe_corrupt(data: bytes, p: float) -> bytes:
    """
    Con cierta probabilidad p, altera un bit aleatorio del mensaje.
    TODO: Implementar alteración aleatoria de un byte/bit.
    """
    pass


# ------------------ PROGRAMA PRINCIPAL ------------------
def main():
    print(f"[Servidor] Escuchando en {HOST}:{PORT}")

    # Crear socket UDP
    # TODO: crear el socket y hacer bind() con (HOST, PORT)

    while True:
        # TODO: recibir datos del cliente con recvfrom()
        # TODO: separar mensaje y CRC
        # TODO: (opcional) aplicar maybe_corrupt() para simular error
        # TODO: recalcular CRC del mensaje
        # TODO: comparar CRC recibido con el recalculado

        # TODO: responder con "ACK <seq>" o "NACK <seq>" según corresponda
        pass


if __name__ == "__main__":
    main()
