import datos as D
import threading
'''
●  Corregir la condición de carrera utilizando Lock. 
●  Proteger conjuntamente la comprobación del stock y el descuento de unidades. 
●  Mantener fuera de la sección crítica todo el código que no necesite protección. 
●  Comprobar que el stock no puede quedar en valores incoherentes.
'''
estanteria = dict(D.STOCK_INICIAL) 
# Creamos una cerradura
cerradura = threading.Lock()

def vender(num_caja):
    global estanteria
    prox_pedido = 0
    while prox_pedido < len(estanteria):
        detalle_pedido = D.PEDIDOS[prox_pedido]
        prox_pedido += 1
        pedido, producto, cantidad = detalle_pedido # Desglosamos lo que tenememos en detalles pedidos
        with cerradura: # Protegemos el descuento de stock dentro de la cerradura solo puede haber uno
            stock =  estanteria[producto]  # Unidades disponibles
            if stock >= cantidad:                
                estanteria[producto] -= cantidad # Le restamos la cantidad
                vendido = True # Bandera de confirmación para los pedidos
            else:
                vendido = False
        print(f"Numero de cajas --> {num_caja}\nPedido --> {pedido}\nProducto --> {producto}\nCantidad del pedido --> {cantidad}\nInventario restante --> {estanteria[producto]}") if vendido else print(f"No hay suficientes unidades d")
            
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
        