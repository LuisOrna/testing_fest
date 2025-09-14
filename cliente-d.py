import socket
import threading
import time

#Variable de control global
servidor_activo = True

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
def recibir_mensajes(cliente):
   global servidor_activo
   while servidor_activo:
       try:
           mensaje = cliente.recv(1024).decode()
           if not mensaje:  #El servidor se cerro
               print("\nEl servidor cerró la conexión")
               servidor_activo = False
               break
           print(f'\n{mensaje}')
           print("tu: ", end="", flush=True) #volver al prompt
       except ConnectionResetError:
           print("\nConexión perdida con el servidor")
           servidor_activo = False
           break
       except Exception:
           #print(f"\nError inesperado: {e}")
           servidor_activo = False
           break

#------------MAIN-----------------------------------------------------------------

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
while True:
   if not servidor_activo:
       # El servidor se desconectó, intentar reconectar
       cliente_nuevo = intentar_reconexion(nombre)
       if cliente_nuevo:
           cliente.close()  # Cerrar el socket viejo
           cliente = cliente_nuevo
           servidor_activo = True
           
           # Crear nuevo thread para recibir mensajes
           thread_recibir = threading.Thread(target=recibir_mensajes, args=(cliente,))
           thread_recibir.start()
       else:
           print("No se pudo reconectar. Saliendo...")
           break
   
   mensaje = input("tu: ")
   if mensaje == 'salir':
       print("Estás saliendo del chat")
       servidor_activo = False
       break
   
   try: 
       cliente.send(mensaje.encode())
   except:
       print("Error enviando mensaje...")
       servidor_activo = False

#Cerrar
cliente.close()
thread_recibir.join(timeout=1)
print("chat cerrado")