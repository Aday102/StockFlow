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
        for reposicion in D.REPOSICIONES:
            if len(reposicion) == 2:
                producto, cantidad = reposicion
            elif len(reposicion) == 3:
                _, producto, cantidad = reposicion
            else:
                raise ValueError("Formaro de reposicioon incorrector.")
            
            time.sleep(1) # Tiempo de preparacion
            with condicion:
                # Añadimos las unidades al inventario
                estanteria[producto] = estanteria.get(producto, 0) + cantidad
                stock_actualizado = estanteria[producto]

                # Mandamos la notificion a las cajas que están esperando
                condicion.notify_all()
            print(f"Almacen: Reposicion de {cantidad} unidades de {producto}.\nStock actual --> {stock_actualizado}.\n")

    finally:
        # Avisamos cuando no queden más reposiciones
        with condicion:
            reposiciones_terminadas = True
            condicion.notify_all()
            
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

    # Iniciamos el almacen
    hilo_almacen.start()

    for z in paquete_hilos:
        z.join()

    # Esperamos a que termine el almacen
    hilo_almacen.join()       

    print("\nINVENTARIO FINAL --> ", estanteria)
    assert all(stock >= 0 for stock in estanteria.values()) # Comprobamos que ninguna producto del inventario se encuentre en negativos.