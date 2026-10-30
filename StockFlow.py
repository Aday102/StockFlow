import datos as D
import threading
'''
●  Crear el inventario a partir de STOCK_INICIAL. 
●  Crear NUM_CAJAS hilos que representen las cajas. 
●  Repartir y procesar los pedidos de PEDIDOS concurrentemente. 
●  Cada venta deberá comprobar si existe stock suficiente y, si existe, descontar las unidades. 
●  Provocar una situación en la que varias cajas compitan por las últimas unidades de un mismo 
producto. 
●  Ejecutar varias veces la aplicación y comprobar si aparecen resultados inconsistentes. 
●  Identificar la sección crítica y documentarla en el README.
'''




# cajeras = D.NUM_CAJAS
# Hilos --> clientes

def vender(num_caja):
    estanteria = dict(D.STOCK_INICIAL) 
    prox_pedido = 0
    while prox_pedido < len(estanteria):
        detalle_pedido = D.PEDIDOS[prox_pedido]
        prox_pedido += 1
        pedido, producto, cantidad = detalle_pedido # Desglosamos lo que tenememos en detalles pedidos
        stock =  estanteria[producto]  # Unidades disponibles

        if stock > cantidad:
            estanteria[producto] -= cantidad # Le restamos la cantidad
            print(f"Numero de cajas --> {num_caja}\nPedido --> {pedido}\nProducto --> {producto}\nCantidad del pedido --> {cantidad}\nInventario restante --> {estanteria[producto]}")


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
