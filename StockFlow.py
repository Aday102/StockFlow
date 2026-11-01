import datos as D
import threading
import time
'''
●  Utilizar NUM_TERMINALES como número máximo de cajas que pueden utilizar simultáneamente un terminal de cobro. 
●  Implementar esta limitación mediante Semaphore. 
●  Mostrar cuándo una caja obtiene y libera un terminal. 
●  Mantener Lock para proteger el inventario: Semaphore y Lock deben resolver problemas distintos. 
'''
estanteria = dict(D.STOCK_INICIAL) 
# Creamos una cerradura
cerradura = threading.Lock()

# Limitamos las cajas que se pueden cobrar
terminales = threading.Semaphore(D.NUM_TERMINALES)


def vender(num_caja):

    
    for prox_pedido in range(num_caja-1, len(D.PEDIDOS), D.NUM_CAJAS): 
        detalle_pedido = D.PEDIDOS[prox_pedido]
        pedido, producto, cantidad = detalle_pedido # Desglosamos lo que tenememos en detalles pedidos
        
        with cerradura: # Protegemos el descuento de stock dentro de la cerradura solo puede haber uno
            stock =  estanteria[producto]  # Unidades disponibles
            if stock >= cantidad:                
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
            
if __name__ == "__main__":
    paquete_hilos = []

    for y in range(D.NUM_CAJAS):
        # Definimos el hilo
        hilos = threading.Thread(target=vender, args=(y+1,))
        paquete_hilos.append(hilos)

    for i in paquete_hilos:
        i.start() #Iniciamos todos los hilos

    for z in paquete_hilos:
        z.join()
        
