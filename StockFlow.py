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
        self.cerradura = threading.RLock()

        self.cerradura_individual = threading.Lock()
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

        self.pedidos_en_procesos = {} # {PEDIDO: ESTADO}

        self.pedidos_rechazados = [] # [Pedidos]

        self.pedidos_cancelados = [] # [pedidos]

        

    # ======= Operaciones =======
    def consultar_stock(self, producto):
        with self.cerradura:
            return self.estanteria.get(producto, 0) # Nos devuelve el valor del producto que le especificamos, si no existe nos devuelve 0.

    def stock_activo(self, producto, cantidad):
        with self.cerradura:
            return self.consultar_stock(producto) >= cantidad

    def realizar_cobro(self, producto, cantidad):
        with self.cerradura:
            self.estanteria[producto] -= cantidad

    def retirar_stock(self, num_caja, producto, cantidad, pedido):
        # Colocamos los pedidos que acaban de llegar y van a comenzar a ser PROCESADOS
        with self.condicion:
            # Primera toma de contacto con el diccionario. Aqui se añaden los pedidos
            self.pedidos_en_procesos[pedido] = "PROCESADOS"
            # ------------------ SECCION CRITICA ------------------
            while not self.stock_activo(producto, cantidad) and not self.reposiciones_terminadas:
                print(f"La caja {num_caja} se encuentra esperando la reposicion de {producto}.\n")
                self.condicion.wait()

            # Volvemos a comprobar el stock
            if self.stock_activo(producto, cantidad):
                # La venta se puede realizar
               
                # Si aún aqui no se ha cancelado este pedido
                if self.pedidos_en_procesos.get(pedido, 0) != "CANCELADO":
                    self.pedidos_en_procesos[pedido] = "COBRANDO" #  AQUI AUN PUEDE CANCELAR Y SU ESTADO ES COBRADNO

                # Se cobraron
                # Si aún aqui no se ha cancelado el pedido se cobra 
                if self.pedidos_en_procesos.get(pedido, 0) != "CANCELADO":
                    self.realizar_cobro(producto, cantidad)
                
                    
                    self.pedidos_en_procesos[pedido] = "COMPLETADO" # AQUI YA NO SE PUEDE COBRAR Y SU ESTADO ES COMPLETADO
                    return True, self.consultar_stock(producto) # Actualizamos el inventario restante y lo mostramos
            # AQUI LOS PEDIDOS SIGUEN PUDIENDO PROCESARSE Y ESTADO ES ESPERANDO
            if self.pedidos_en_procesos.get(pedido, 0) != "CANCELADO":
                self.pedidos_en_procesos[pedido] = "ESPERANDO"

                # Puede pasar que sea por stock
                return False, self.consultar_stock(producto)

    def reponer_stock(self, producto, cantidad):
        with self.condicion:
            # ------------------ SECCION CRITICA ------------------
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
        # ------------------ SECCION CRITICA ------------------
        with self.cerradura:
            stock = self.consultar_stock(producto)
            if stock < 0:
                self.productos_negativos.append(producto)
            elif stock == 0:
                self.productos_agotados.append(producto)
            return stock
    
    def cancelar_pedido(self, pedido):
        with self.cerradura_individual:
            if self.pedidos_en_procesos.get(pedido, 0) == "COMPLETADO":
                self.pedidos_rechazados.append(pedido) # PED-001
            else:
                self.pedidos_en_procesos[pedido] = "CANCELADO"
                self.pedidos_cancelados.append(pedido) # PED-001

            
        
        



# Creamos el objeto del gesto y todo lo necesario pa su funcionamiento
gestor = GestorInventario(D.STOCK_INICIAL)
terminales = threading.Semaphore(D.NUM_TERMINALES)
barrera = threading.Barrier(D.NUM_REVISORES+1) # 5 hilos en total.
cerradura = threading.Lock()



def vender(num_caja):
    for prox_pedido in range(num_caja-1, len(D.PEDIDOS), D.NUM_CAJAS):
        # =================== Operaciones de pedidos =================================
        pedido, producto, cantidad =  D.PEDIDOS[prox_pedido]# Desglosamos lo que tenememos en detalles pedidos
        vendido, inventario_restante = gestor.retirar_stock(num_caja, producto, cantidad, pedido)

        if vendido:
            print(f"Numero de cajas --> {num_caja}\nPedido --> {pedido}\nProducto --> {producto}\nCantidad del pedido --> {cantidad}\nInventario restante --> {inventario_restante}\n")
            with terminales:
                print(f"La caja {num_caja} ha obtenido una terminal de cobro.\n")
                time.sleep(D.TIEMPO_COBRO)
                print(f"La caja {num_caja} ya ha terminado y ha liberado la terminal.\n")
        else:
            print(f"Caja {num_caja}: pedido {pedido} rechazado. No hay suficientes unidades de {producto}.\n")


def reponer():

    try:
        for identificacion, producto, cantidad in D.REPOSICIONES:
            time.sleep(D.TIEMPO_REPOSICION) # Tiempo de preparacion
            stock_actualizado= gestor.reponer_stock(producto, cantidad)
            print(f"Almacen: Reposicion de {cantidad} unidades de {producto}.\nStock actual --> {stock_actualizado}.\n")
          
    finally:
        # Avisamos al gestor que no quedan más reposiciones
        gestor.terminar_reposiciones()
def revisar(num_revisor):
    catalogo = gestor.obtener_catalogo()

    # Usamos el mismo reparto que el de las cajas
    for prox_producto in range(num_revisor-1, len(catalogo), D.NUM_REVISORES):
        producto, _ = catalogo[prox_producto] # prox_producto es numero de iteracion del range, los otros 2 no se van cambiando, solo se cambia el prox_producto, por lo tanto esto sería tal que producto1, producto2, producto3, producto4, producto5, producto6, producto7, producto8, producto9, producto10
        stock = gestor.registrar_revision(producto)
        print(f"Revisor {num_revisor} comprobando el producto: {producto} --> {stock} unidades.\n")
    print(f"El revisor {num_revisor} ha terminado y esta esperando en la barrera.\n")
    barrera.wait() # Le indicamos que se quede aqui hasta que llegan todos los demás.
def cancelar():
    rechazados = 0
    with cerradura:
        for prox_cancelacion in range(len(D.CANCELACIONES)):
            id_cancelacion, id_pedido, segundos = D.CANCELACIONES[prox_cancelacion] # Desglosamos las cancelaciones
            time.sleep(segundos)
            # =================== Operaciones de cancelaciones ===================================

            respuesta = gestor.cancelar_pedido(id_pedido) # True --> Cancelado | False --> Rechazado
            if not respuesta:
                rechazados += 1

if __name__ == "__main__":
    paquete_hilos = []

    for y in range(D.NUM_CAJAS):
        # Definimos el hilo
        hilos = threading.Thread(target=vender, args=(y+1,))
        paquete_hilos.append(hilos)
    
    for w in range(0,1):
        hilo_cancelar = threading.Thread(target=cancelar)
        paquete_hilos.append(hilo_cancelar)




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
          f"Productos agotados --> {gestor.productos_agotados if gestor.productos_agotados else 'Ninguno'}\n"
          f"Producto en negativos --> {gestor.productos_negativos if gestor.productos_negativos else 'Ninguno'}\n"
          f"Productos de cancelacion rechazados --> {gestor.pedidos_rechazados if gestor.pedidos_rechazados else 'Ninguno'}\n"
          f"Pedidos cancelados --> {gestor.pedidos_cancelados if gestor.pedidos_cancelados else 'Ninguno'}")

    print(f"")
    for revisor in paquete_revisados:
        revisor.join()
    assert not gestor.productos_negativos # Verificamos que no hay productos en negativo dentro del inventario