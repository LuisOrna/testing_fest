import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from clientef import enviar_mensaje


def test_enviar_mensaje():
    from unittest.mock import Mock

    #Mock del socket cliente
    mock_cliente = Mock()
    mensaje = "mensaje de prueba"

    #pruebo la funcion, que aun no existe
    resultado = enviar_mensaje(mock_cliente, mensaje)

    #Resultados
    mock_cliente.send.assert_called_once_with(mensaje.encode())
    assert resultado == True