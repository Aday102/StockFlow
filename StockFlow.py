import datos as D
import threading
import time
'''
●  Organizar la gestión del inventario en una clase. 
●  Diseñar al menos una operación protegida que invoque otra operación protegida del mismo gestor. 
●  Sustituir el mecanismo adecuado por RLock para permitir la reentrada del mismo hilo. 
●  Explicar en el README por qué RLock es necesario en ese diseño.
'''

class GestorInventario:
    def __init__(self, stock_inicial):

        self.estanteria = dict(stock_inicial) 
        # Creamos una cerradura
        self.cerradura = threading.Lock()

        # Limitamos las cajas que se pueden cobrar
        self.terminales = threading.Semaphore(D.NUM_TERMINALES)

        # Creamos una condicion utilizando la misma cerradura del inventario.
        self.condicion = threading.Condition(self.cerradura)

        # Indicamos si el almacen ha terminado las reposiciones
        self.reposiciones_terminadas = False

        # La barrera la tienen que cruzar los revisores más el hilo principal
        self.barrera = threading.Barrier(D.NUM_REVISORES + 1)

        # Resultados de las revisiones
        self.productos_agotados = []
        self.productos_negativos = []

    # ======= Operaciones =======
    def consultar_stock(self, producto):
        with self.cerradura:
            return self.estanteria.get(producto, 0)

    def stock_activo(self, producto, cantidad):
        with self.cerradura:
            return self.consultar_stock(producto) >= cantidad

    def retirar_stock(self, num_caja, producto, cantidad):
        with self.condicion:
            while not self.stock_activo(producto, cantidad) and not self.reposiciones_terminadas:
                print(f"La caja {num_caja} se encuentra esperando la reposicion de {producto}.\n")
                self.condicion.wait()

            # Volvemos a comprobar el stock
            if self.stock_activo(producto, cantidad):
                self.estanteria[producto] -= cantidad
                return True, self.consultar_stock(producto) # Actualizamos el inventario restante y lo mostramos
            return False, self.consultar_stock(producto)

    def reponer_stock(self, producto, cantidad):
        with self.condicion:
            self.estanteria[producto] = self.consultar_stock(producto) + cantidad
            self.condicion.notify_all() # Comunicamos que las cajas están esperando
            return self.consultar_stock(producto)

    def terminar_reposiciones(self):
        with self.condicion:
            self.reposiciones_terminadas = True
            self.condicion.notify_all()

    def obtener_catalogo(self):
        with self.cerradura:
            return list(self.estanteria.items()) # Hacemos una copua en una lista para repartir posiciones.


    def registrar_revision(self, producto):
        with self.cerradura:
            stock = self.consultar_stock(producto)
            if stock < 0:
                self.productos_negativos.append(producto)
            elif stock == 0:
                self.productos_agotados.append(producto)
            return stock

# Creamos el objeto del gesto y todo lo necesario pa su funcionamiento
gestor = GestorInventario(D.STOCK_INICIAL)
terminales = threading.Semaphore(D.NUM_TERMINALES)
barrera = threading.Barrier(D.NUM_REVISORES+1)




def vender(num_caja):
    for prox_pedido in range(num_caja-1, len(D.PEDIDOS), D.NUM_CAJAS): 
        pedido, producto, cantidad =  D.PEDIDOS[prox_pedido]# Desglosamos lo que tenememos en detalles pedidos
        vendido, inventario_restante = gestor.retirar_stock(num_caja, producto, cantidad)

        if vendido:
            print(f"Numero de cajas --> {num_caja}\nPedido --> {pedido}\nProducto --> {producto}\nCantidad del pedido --> {cantidad}\nInventario restante --> {inventario_restante}\n")
            with terminales:
                print(f"La caja {num_caja} ha obtenido una terminal de cobro.\n")
                time.sleep(2)
                print(f"La caja {num_caja} ya ha terminado y ha liberado la terminal.\n")
        else:
            print(f"Caja {num_caja}: pedido {pedido} rechazado. No hay suficientes unidades de {producto}.\n")
def reponer():
    global reposiciones_terminadas

    try:
        for identificacion, producto, cantidad in D.REPOSICIONES:
            time.sleep(1) # Tiempo de preparacion
            stock_actualizado= gestor.reponer_stock(producto, cantidad)
            print(f"Almacen: Reposicion de {cantidad} unidades de {producto}.\nStock actual --> {stock_actualizado}.\n")
          
    finally:
        # Avisamos al gestor que no quedan más reposiciones
        gestor.terminar_reposiciones()
def revisar(num_revisor):
    catalogo = gestor.obtener_catalogo()

    # Usamos el mismo reparto que el de las cajas
    for prox_producto in range(num_revisor-1, len(catalogo), D.NUM_REVISORES):
        producto, _ = catalogo[prox_producto]
        stock = gestor.registrar_revision(producto)
        print(f"Revisor {num_revisor} comprobando el producto: {producto} --> {stock} unidades.\n")
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
          f"INVENTARIO FINAL --> {gestor.estanteria}\n"
          f"Productos agotados --> {gestor.productos_agotados if gestor.productos_agotados else 'Ninguno'}"
          f"Producto en negativos --> {gestor.productos_negativos if gestor.productos_negativos else 'Ninguno'}")
    for revisor in paquete_revisados:
        revisor.join()
    assert not gestor.productos_negativos # Verificamos que no hay productos en negativo dentro del inventario