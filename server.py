#Dependencias
import socket
import threading

#Globales
clientes = []
nombres = {}

def registrar_cliente(conexion):
    '''registra el nombre del cliente antes de entrar'''
    try:
        nombre = conexion.recv(1024).decode()
        clientes.append(conexion) 
        nombres[conexion] = nombre
        return True
    except:
        print("nombre no pudo ser registrado (111)")
        return False


def broadcast(mensaje, conexion_origen=None):
    """Envía mensaje a todos excepto al origen"""
    for cliente in clientes[:]:
        if cliente != conexion_origen:  # No enviarte a ti mismo
            try:
                cliente.send(mensaje)
            except Exception as error:
                print(f"no se pudo enviar mensaje al cliente {nombres[cliente]} eror{error} (100)")
                pass


def notificar_entrada(nombre):
    '''notifica que un cliente ingreso'''
    print(f'{nombre} entro al chat')
    try:
        broadcast(f"{nombre} entro al chat".encode())
        return
    except Exception as error:
        print(f'error al notificar la entrada de {nombre}, error {error} (144)')
        return


def procesar_mensajes(conexion):
    '''ayuda a recibir los mensajes de los clientes en un bucle'''
    while True:
        try:
            mensaje= (conexion.recv(1024)).decode() #Dejo en mensaje en datos
            if not mensaje: 
                print(f"cliente {nombres[conexion]} desconectado (122)")
                #notificar_salida(conexion) #Se notifica de la salida del cliente 
                #limpiar_cliente(conexion) #Se limpia el cliente
                break
            broadcast(f"{nombres[conexion]}: {mensaje}".encode(), conexion) #deberia estar en datos

        except ConnectionResetError: #desconexion cuendo el cliente 
            break
            
        except Exception as error: #otros errores
            print(f"error {error} al procesar el mensaje de {nombres[conexion]} (133)")
            break

def notificar_salida(conexion):
    '''hace broadcasrt cuando alguien sale'''
    if conexion in clientes:
        nombre = nombres.get(conexion, "Usuario")
        print(f"{nombre} salió del chat")
        #print(f"{nombres[conexion]} salio del chat") # la opcion con get es mas segura
        broadcast(f"{nombres[conexion]} salio del chat".encode(), conexion)


def limpiar_cliente(conexion):
    '''una vez que un cliente se desconecta, limpia ese cliente de la lista, del dicionario, threads y cierra el socket'''
    if conexion in clientes:
        clientes.remove(conexion) #Saco de la lista de conexiones
    if conexion in nombres:
        nombres.pop(conexion) #Saco de la lista de nombres
    conexion.close()


def atender_cliente(conexion):
    '''organiza el flujo de todas las funciones y asi facilita la creacion del hijo'''

    if registrar_cliente(conexion) == False: #En caso de fallar el registro de nombre
        conexion.close()
        return #Para salir de la funcion
    
    #Registro de nombre exitoso
    notificar_entrada(nombres[conexion])

    #Que se procesen los mensajes
    procesar_mensajes(conexion)

    #Guardo el nombre, esto para tenerlo almacenado porque se perdera al limpiar
    #nombre_cliente = nombres.get(conexion, "usuario")

    #Salida
    notificar_salida(conexion)

    #Limpieza
    limpiar_cliente(conexion)




#-------------------MAIN-------------------------------------------------------------------------------------------------
servidor = socket.socket()
servidor.bind(('localhost', 9999))
servidor.listen(4)
print("esperando conexion...")

#Flujo
while True:
    conexion,_ = servidor.accept()

    #Se crea al thread
    thread = threading.Thread(target=atender_cliente, args=(conexion,))
    thread.start()

