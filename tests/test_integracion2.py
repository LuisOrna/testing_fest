import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import socket
import threading
import time
from servidor import iniciar_servidor, clientes, nombres

#Con este test intento probar mas una conexion trayecdo mas componentes desde el servidor
def test_conversacion_dos_clientes():
    #limpio
    clientes.clear()
    nombres.clear()
    
    #arranco servidor con un hilo
    servidor_thread = threading.Thread(target=iniciar_servidor, daemon=True)
    servidor_thread.start()
    time.sleep(1)  # es para evitar que me de error y se pueda iniciar todo  
    
    # conecto peimer  cliente
    cliente1 = socket.socket()
    cliente1.connect(('localhost', 9999))
    cliente1.send(b"Luis") 
    time.sleep(0.5)

    # conecto cliente2
    cliente2 = socket.socket()
    cliente2.connect(('localhost', 9999))
    cliente2.send(b"Carlos")
    time.sleep(0.5)

    # tiro mensajes
    cliente1.send(b"saludos soy Luis desde el 1")

    # verifico que llego
    mensaje_rec = []
    cliente2.settimeout(1)
    try: 
        while True:
            mens = cliente2.recv(1024).decode()
            if mens:
                mensaje_rec.append(mens)
    except socket.timeout:
        pass

    print(f'Carlos recibio: {mensaje_rec}')

    #verificaciones
    assert len(mensaje_rec) >= 1
    assert "saludos soy Luis desde el 1" in mensaje_rec[-1]
    
    # 7. Limpieza
    cliente1.close()
    cliente2.close()