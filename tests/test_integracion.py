import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from unittest.mock import Mock
from servidor import clientes, nombres, broadcast, registrar_cliente, limpiar_cliente

#Creo inicialmente un test para ver la atencion con dos clientes en simultaneo
def test_dos_clientes_simultaneos():
    #Limpieza inicial
    clientes.clear()
    nombres.clear()

    #Creo dos clientes
    cliente_1 = Mock()
    cliente_2 = Mock()

    #Simulo que recv() devuelve los nombres
    cliente_1.recv.return_value = b"Usuario 1"
    cliente_2.recv.return_value = b"Usuario 2"

    #Registro a ambos clientes
    assert registrar_cliente(cliente_1) == True
    assert registrar_cliente(cliente_2) == True

    #Verificar que ambos estan en las listas
    assert len(clientes) == 2
    assert cliente_1 in clientes 
    assert cliente_2 in clientes
    assert nombres[cliente_1] == "Usuario 1"
    assert nombres[cliente_2] == "Usuario 2"


#2 Mensaje entre Clientes
def test_mensaje_entre_clientes():
    #Limpiar estado
    clientes.clear()
    nombres.clear()

    #Creo los clientes
    cliente_1 = Mock()
    cliente_2 = Mock()

    #Creacion manual, porque ya eso probe en el anterior
    clientes.append(cliente_1)
    clientes.append(cliente_2)
    nombres[cliente_1] = "Usiario 1"
    nombres[cliente_2] = "Usuario 2"

    #Hago que el el usuario 1 escriba
    mensaje = b"Hola yo soy el Usuario 1"
    broadcast(mensaje=mensaje, conexion_origen=cliente_1)

    #Verificaciones
    cliente_1.send.assert_not_called() #para saber que el 1 no recibe su propio mensaje
    cliente_2.send.assert_called_once_with(mensaje) #Cliente 2 si recibe en mensaje


#2 ahora pruebo con 3 clientes
def test_mensaje_3_cleintes():
    #Primero que nada limpio esto
    clientes.clear()
    nombres.clear()

    #Creo los clientes Mock
    cliente_1 = Mock()
    cliente_2 = Mock()
    cliente_3 = Mock()

    #Agrego manualmente
    clientes.append(cliente_1)
    clientes.append(cliente_2)
    clientes.append(cliente_3)
    nombres[cliente_1] = "User 1"
    nombres[cliente_2] = "User 2"
    nombres[cliente_3] = "User 3"

    #Hago que el usuario 2 escriba
    mensaje = b"Hola, soy el numero 2"
    broadcast(mensaje=mensaje, conexion_origen=cliente_2)

    #Verificaciones
    cliente_2.send.assert_not_called() #verifico que el 2 no recibio su mismo mensaje
    cliente_1.send.assert_called_once_with(mensaje)
    cliente_3.send.assert_called_once_with(mensaje)        


#TEST DE DESCONEXION
def test_cliente_desconecta_normal():
    clientes.clear()
    nombres.clear()

    #creo mock de conexion
    conexion = Mock()
    clientes.append(conexion)
    nombres[conexion] = "Conexion 1"

    #Pruebo a la funcion
    limpiar_cliente(conexion=conexion)

    #Verificaciones
    assert conexion not in clientes
    assert conexion not in nombres
    conexion.close.assert_called_once()
    

#Test para desconexion inesperada
def test_servidor_continua_despues_desconexion_inesperada():
    clientes.clear()
    nombres.clear()

    cliente_1 = Mock()
    cliente_2 = Mock()
    cliente_3 = Mock()

    #Agregar a las listas
    clientes.append(cliente_1)
    clientes.append(cliente_2)
    clientes.append(cliente_3)
    nombres[cliente_1] = "user1"
    nombres[cliente_2] = "user2"
    nombres[cliente_3] = "user3"

    # Cliente2 se desconecta
    limpiar_cliente(cliente_2)
    
    # Verificar que cliente2 ya no está
    assert cliente_2 not in clientes
    assert cliente_2 not in nombres
    
    # Verificar que el servidor sigue funcionando con los otros
    mensaje = b"Mensaje despues de desconexion"
    broadcast(mensaje, cliente_1)
    
    # Solo cliente3 debe recibir el mensaje
    cliente_1.send.assert_not_called()  # origen, no debe recibir
    cliente_3.send.assert_called_once_with(mensaje)  # debe recibir


def test_desconexion_repentina_durante_broadcast():
    clientes.clear()
    nombres.clear()
    
    # Crear 2 clientes
    cliente1 = Mock()
    cliente2 = Mock()
    
    # cliente1 normal, cliente2 va a fallar
    cliente2.send.side_effect = ConnectionResetError("Conexión perdida")
    
    clientes.append(cliente1)
    clientes.append(cliente2)
    nombres[cliente1] = "User1"
    nombres[cliente2] = "User2"
    
    # Enviar mensaje
    mensaje = b"Test mensaje"
    broadcast(mensaje)
    
    # verifo que se recibio mensaje normal.
    cliente1.send.assert_called_once_with(mensaje)
    
#Otra prueba para ver desconexion repentina
def test_desconexion_repentina_durante_broadcast():
    clientes.clear()
    nombres.clear()
    
    # Crear 2 clientes
    cliente1 = Mock()
    cliente2 = Mock()
    
    # Cliente2 falla cuando le envían mensaje
    cliente2.send.side_effect = BrokenPipeError("Conexión rota")
    
    # Agregar a las listas
    clientes.append(cliente1)
    clientes.append(cliente2)
    nombres[cliente1] = "User1" 
    nombres[cliente2] = "User2"
    
    # Primer broadcast - cliente2 va a fallar
    mensaje1 = b"Primer mensaje"
    broadcast(mensaje1)
    
    # LA PREGUNTA CLAVE: ¿Cliente2 sigue en la lista?
    print(f"\nClientes después del fallo: {len(clientes)}")
    print(f"Cliente2 sigue en lista: {cliente2 in clientes}")
    
    # Segundo broadcast - ¿reintenta con cliente2?
    mensaje2 = b"Segundo mensaje"
    broadcast(mensaje2)
    
    # Verificaciones básicas
    assert cliente1.send.call_count == 2  # Debe recibir ambos mensajes


#Despues de reparado
def test_desconexion_repentina_durante_broadcast():
    clientes.clear()
    nombres.clear()
    
    cliente1 = Mock()
    cliente2 = Mock()
    cliente2.send.side_effect = BrokenPipeError("Conexión rota")
    
    clientes.append(cliente1)
    clientes.append(cliente2)
    nombres[cliente1] = "User1" 
    nombres[cliente2] = "User2"
    
    # Primer broadcast - cliente2 falla
    broadcast(b"Primer mensaje")
    
    # Verificar que cliente2 fue limpiado
    assert len(clientes) == 1
    assert cliente2 not in clientes
    assert cliente2 not in nombres
    
    # Segundo broadcast - solo cliente1 activo
    broadcast(b"Segundo mensaje")
    
    # Cliente1 recibe ambos mensajes
    assert cliente1.send.call_count == 2