# Importar el módulo servidor
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from servidor import broadcast, clientes, nombres, registrar_cliente

#Test para probar broadcast
def test_broadcast_basico():
    #Limpiar estado anterior
    clientes.clear()
    nombres.clear()

    #Crear los cliente simulados 
    from unittest.mock import Mock
    cliente1 = Mock()
    cliente2 = Mock()

    #Agregar a las listas Globales
    clientes.append(cliente1)
    clientes.append(cliente2)
    nombres[cliente1] = 'Usuario1'
    nombres[cliente2] = 'Usuario2'

    #Probar el Broadcast
    mensaje = b'Hola mundo'
    broadcast(mensaje, cliente1)

    #Verificar Resultados
    cliente1.send.assert_not_called()
    cliente2.send.assert_called_once_with(mensaje)
    
#Test para Registrar Cliente
def test_registrar_cliente_exitoso():

    #Primero se limpia 
    clientes.clear()
    nombres.clear()

    #Crear Mock de Conexion
    from unittest.mock import Mock
    mock_conexion = Mock()
    mock_conexion.recv.return_value = b"TestUser" #Simula que recv() devuelve "TestUser"

    #Probar funcion
    resultado = registrar_cliente(mock_conexion)


    #Verificar Resultados
    assert resultado == True
    assert mock_conexion in clientes
    assert nombres[mock_conexion] == "TestUser"
    mock_conexion.recv.assert_called_once_with(1024)

    

#Test Negativo, es decir quiero comprpbar que tambien cuando falla me devuelve lo que corresponde
def test_registrar_cliente_error():
    #Limpiar estado
    clientes.clear()
    nombres.clear()

    #Crear un Mock que simula error en Recv()
    from unittest.mock import Mock
    mock_conexion = Mock()
    mock_conexion.recv.side_effect = Exception("Error de Conexion") #Simula que recv() falla

    #Pruebo la funcion
    resultado = registrar_cliente(mock_conexion)

    #Verifico los resultados
    assert resultado == False
    assert mock_conexion not in clientes #No debe estar en la lista
    assert mock_conexion not in nombres #no deberia estar en el Dict

