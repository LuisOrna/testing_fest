import socket
import threading
import time

#Variable de control global
servidor_activo = True
cliente = None  # Declarar como global

def intentar_reconexion(nombre):
   for intento in range(3):
       print(f"\nIntentando reconectar... ({intento + 1}/3)")
       try:
           nuevo_cliente = socket.socket()
           nuevo_cliente.connect(('localhost', 9999))
           nuevo_cliente.send(nombre.encode())
           print("¡Reconectado exitosamente!")
           return nuevo_cliente
       except:
           print(f"Intento {intento + 1} falló")
           if intento < 2:  # No esperar después del último intento
               time.sleep(5)
   
   print("No se pudo reconectar después de 3 intentos")
   return None

#Funcion para que el cliente reciba mensajes
def recibir_mensajes(cliente_local):
   global servidor_activo, cliente
   while True:
       try:
           mensaje = cliente_local.recv(1024).decode()
           if not mensaje:
               print("\nEl servidor cerró la conexión")
               break
           print(f'\n{mensaje}')
           print("tu: ", end="", flush=True)
       except:
           
           break
   
   # Cuando sale del bucle, intenta reconectar
   if servidor_activo:  # Solo si no es salida manual
       cliente_nuevo = intentar_reconexion(nombre)
       if cliente_nuevo:
           cliente_local.close()
           cliente = cliente_nuevo
           # Llamarse a sí misma recursivamente
           recibir_mensajes(cliente)
       else:
           servidor_activo = False

def enviar_mensaje(cliente_socket, mensaje):
    """Envía un mensaje a través del socket cliente"""
    try:
        cliente_socket.send(mensaje.encode())
        return True
    except:
        return False

#------------MAIN-----------------------------------------------------------------
if __name__ == '__main__':
    
    #Cliente
    cliente = socket.socket()
    nombre = input("Ingrese su nombre: ")

    #Hago que se conecte
    cliente.connect(('localhost', 9999))
    cliente.send(nombre.encode())

    print('\nconectado al servidor\n')

    #Thread para recibir mensajes
    thread_recibir = threading.Thread(target=recibir_mensajes, args=(cliente,))
    thread_recibir.start()

    #Enviar mensaje
    print("Conectado al chat. Escribe 'salir' para terminar.\n")
    while servidor_activo:
        mensaje = input("tu: ")
        if mensaje == 'salir':
            print("Estás saliendo del chat")
            servidor_activo = False
            break

        if not enviar_mensaje(cliente, mensaje):
            print("Error enviando mensaje...")

    '''
    try: 
        cliente.send(mensaje.encode())
    except:
        print("Error enviando mensaje...")
        # No cambiar servidor_activo aquí, dejar que el hilo de recepción maneje
        '''

    #Cerrar
    cliente.close()
    thread_recibir.join(timeout=1)
    print("chat cerrado")