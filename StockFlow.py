import datos as D
import threading
import time
'''
●  Crear NUM_REVISORES hilos de revisión. 
●  Repartir entre ellos la comprobación final del catálogo. 
●  Utilizar Barrier para impedir que continúe el cierre hasta que todos hayan terminado su revisión. 
●  Mostrar el resumen final solo después de superar la barrera.
'''
estanteria = dict(D.STOCK_INICIAL) 
# Creamos una cerradura
cerradura = threading.Lock()

# Limitamos las cajas que se pueden cobrar
terminales = threading.Semaphore(D.NUM_TERMINALES)

# Creamos una condicion utilizando la misma cerradura del inventario.
condicion = threading.Condition(cerradura)

# Indicamos si el almacen ha terminado las reposiciones
reposiciones_terminadas = False

# La barrera la tienen que cruzar los revisores más el hilo principal
barrera = threading.Barrier(D.NUM_REVISORES + 1)

# Resultados de las revisiones
productos_agotados = []
productos_negativos = []


def vender(num_caja):
    for prox_pedido in range(num_caja-1, len(D.PEDIDOS), D.NUM_CAJAS): 
        detalle_pedido = D.PEDIDOS[prox_pedido]
        pedido, producto, cantidad = detalle_pedido # Desglosamos lo que tenememos en detalles pedidos
        
        with condicion: # Protegemos el acceso al inventario canbiamdo 'cerradura' por 'condicion'
            
            # Esperammos mientras no haya stock y queden reposiciones
            while estanteria.get(producto, 0) < cantidad and not reposiciones_terminadas:
                print(f"La caja {num_caja} se encuentra esperando reposición de {producto}.")
                condicion.wait() # Hace que la caja se duerma mientras se libera el Lock y esperamos a una notificación

            if estanteria.get(producto, 0) >= cantidad:
                estanteria[producto] -= cantidad # Le restamos la cantidad
                vendido = True # Bandera de confirmación para los pedidos
            else:
                vendido = False
        if vendido:
            print(f"Numero de cajas --> {num_caja}\nPedido --> {pedido}\nProducto --> {producto}\nCantidad del pedido --> {cantidad}\nInventario restante --> {estanteria[producto]}\n")

            with terminales:
                print(f"La caja {num_caja} ha obtenido una terminal de cobro.\n")
                time.sleep(2)
                print(f"La caja {num_caja} ya ha terminado y ha liberado la terminal de cobro.\n")
        else: 
            print(f"No hay suficientes unidades de {producto}")

def reponer():
    global reposiciones_terminadas

    try:
        for identificacion, producto, cantidad in D.REPOSICIONES:
            time.sleep(1) # Tiempo de preparacion
            with condicion:
                # Añadimos las unidades al inventario
                estanteria[producto] = estanteria.get(producto, 0) + cantidad
                stock_actualizado = estanteria[producto]
                condicion.notify_all() # Mandamos la notificion a las cajas que están esperando
            print(f"Almacen: Reposicion de {cantidad} unidades de {producto}.\nStock actual --> {stock_actualizado}.\n")

    finally:
        # Avisamos cuando no queden más reposiciones
        with condicion:
            reposiciones_terminadas = True
            condicion.notify_all()


def revisar(num_revisor):
    catalogo = list(estanteria.items()) # Convertimos el inventario a listas pa poder trabajar con las posiciones

    # Usamos el mismo reparto que el de las cajas
    for prox_producto in range(num_revisor-1, len(catalogo), D.NUM_REVISORES):
        producto, stock = catalogo[prox_producto]
        print(f"Revisor {num_revisor} comprobando el producto: {producto} --> {stock} unidades.\n")

        with cerradura:
            if stock < 0:
                productos_negativos.append(producto)
            elif stock == 0:
                productos_agotados.append(producto)
    print(f"El revisor {num_revisor} ha terminado y esta esperando en la barrera.\n")
    barrera.wait() # Le indicamos que se quede aqui hasta que llegan todos los demás.


if __name__ == "__main__":
    paquete_hilos = []

    for y in range(D.NUM_CAJAS):
        # Definimos el hilo
        hilos = threading.Thread(target=vender, args=(y+1,))
        paquete_hilos.append(hilos)

    # Creamos el hilo de almacen
    hilo_almacen = threading.Thread(target=reponer)

    for i in paquete_hilos:
        i.start() #Iniciamos todos los hilos
   
    hilo_almacen.start() # Iniciamos el almacen

    for z in paquete_hilos:
        z.join()
    
    hilo_almacen.join() # Esperamos a que termine el almacen

    paquete_revisados = []
    for e in range(D.NUM_REVISORES):
        revisor = threading.Thread(target=revisar, args=(e+1, ))
        paquete_revisados.append(revisor)

    for revisor in paquete_revisados:
        revisor.start()

    barrera.wait() # El cierre no continua hasta que todos los revisores lleguen a la barrera.

    # Solo llegamos aqui cuando se supera la barrera
    print("\n===== RESUMEN =====\n"
          f"INVENTARIO FINAL --> {estanteria}\n"
          f"Productos agotados --> {productos_agotados if productos_agotados else 'Ninguno'}"
          f"Producto en negativos --> {productos_negativos if productos_negativos else 'Ninguno'}")

    assert not productos_negativos # Verificamos que no hay productos en negativo dentro del inventario