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




estanteria = dict(D.STOCK_INICIAL) 
cajeras = D.NUM_CAJAS
# Hilos --> clientes
print(estanteria)
print(cajeras)
def vender(num_caja):
    prox_pedido = 0
    while prox_pedido < len(estanteria):
        detalle_pedido = D.PEDIDOS[prox_pedido]
        prox_pedido += 1
        pedido, producto, cantidad = detalle_pedido # Desglosamos lo que tenememos en detalles pedidos
        stock =  estanteria[1]  # Unidades disponibles

        if stock > cantidad:
            estanteria[producto] -= cantidad # Le restamos la cantidad
            print(f"Pedido --> {pedido}\nProducto --> {producto}\nCantidad del pedido --> {cantidad}\nInventario restante --> {estanteria[0]}")
        
            












# pedidos = [threading.Thread(target=stock_disponible, args=) for _ in range(D.NUM_CAJAS)]   