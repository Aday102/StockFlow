# ===== IMPORTACIONES =====

import datos as D
import threading
import time

# ===== CLASE GESTOR DE INVENTARIO =====

class GestorInventario:

    # ===== INICIALIZACIÓN Y MECANISMOS DE SINCRONIZACIÓN =====

    def __init__(self, stock_inicial):

        self.estanteria = dict(stock_inicial) 
        # Creamos una cerradura
        self.cerradura = threading.RLock()

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

        # Variables de la modificación de la estadistica de ventas
        self.contador_pedidos_vendidos = 0
        self.contador_pedidos_rechazados = 0




    # ===== CONSULTA Y COMPROBACIÓN DE STOCK =====

    def consultar_stock(self, producto):
        with self.cerradura:
            return self.estanteria.get(producto, 0) # Nos devuelve el valor del producto que le especificamos, si no existe nos devuelve 0.

    def stock_activo(self, producto, cantidad):
        with self.cerradura:
            return self.consultar_stock(producto) >= cantidad


    # ===== VENTA Y CONTROL DEL TIEMPO DE ESPERA =====

    def retirar_stock(self, num_caja, producto, cantidad):
        # Parametros del control del tiempo de espera
        inicio = time.monotonic()
        tiempo_max = 5

        with self.condicion:
            # ------------------ SECCION CRITICA ------------------
            while not self.stock_activo(producto, cantidad) and not self.reposiciones_terminadas:
                # Conttrol del tiempo
                transcurrido = time.monotonic() - inicio
                restante = transcurrido - tiempo_max

                # En este punto tenemos todos los datos necesarios para saber cuanto tiempo a transcurrido
                if restante <= 0:
                    print(f"{'\033[31m'}Se ha pasado el tiempo maximo de espera.{'\033[0m'}")
                    break

                print(f"La caja {num_caja} se encuentra esperando la reposicion de {producto}.\n")
                self.condicion.wait()

            # Volvemos a comprobar el stock
            if self.stock_activo(producto, cantidad):
                # La venta se puede realizar
                self.estanteria[producto] -= cantidad
                self.sumarPedidosVendidos()
                return True, self.consultar_stock(producto) # Actualizamos el inventario restante y lo mostramos
            # Si se rechaza porque no se puede realizar la venta
            self.sumarPedidoRechazado()
            return False, self.consultar_stock(producto)


    # ===== REPOSICIÓN DE INVENTARIO =====

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


    # ===== CATÁLOGO Y REVISIÓN DE INVENTARIO =====

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
    

    # ===== RECUENTO TOTAL DE UNIDADES =====

    def unidades_totales(self) -> int:
        conteo = 0
        with self.cerradura:
            for producto, cantidad in self.estanteria.items():
                conteo += cantidad
            return conteo    

    # ===== ESTADÍSTICAS DE VENTAS =====

    def estadisticas_ventas(self):
        pedidos_procesados = self.contador_pedidos_vendidos + self.contador_pedidos_rechazados
        return self.contador_pedidos_vendidos, self.contador_pedidos_rechazados, pedidos_procesados

    def sumarPedidoRechazado(self):
        with self.cerradura:
            self.contador_pedidos_rechazados += 1

    def sumarPedidosVendidos(self):
        with self.cerradura:
            self.contador_pedidos_vendidos += 1



        

# ===== INICIALIZACIÓN DEL GESTOR Y RECURSOS COMPARTIDOS =====

# Creamos el objeto del gesto y todo lo necesario pa su funcionamiento
gestor = GestorInventario(D.STOCK_INICIAL)
terminales = threading.Semaphore(D.NUM_TERMINALES)
barrera = threading.Barrier(D.NUM_REVISORES+1) # 5 hilos en total.





# ===== HILO DE CAJA: VENTAS Y COBROS =====

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
            if inventario_restante <= 3:
                print(f"{'\033[33m'}AVISO: Stock bajo de {producto}.{'\033[0m'}")
        else:
            print(f"Caja {num_caja}: pedido {pedido} rechazado. No hay suficientes unidades de {producto}.\n")

# ===== HILO DE ALMACÉN: REPOSICIONES =====

def reponer():

    try:
        for identificacion, producto, cantidad in D.REPOSICIONES:
            time.sleep(1) # Tiempo de preparacion
            stock_actualizado= gestor.reponer_stock(producto, cantidad)
            print(f"Almacen: Reposicion de {cantidad} unidades de {producto}.\nStock actual --> {stock_actualizado}.\n")
          
    finally:
        # Avisamos al gestor que no quedan más reposiciones
        gestor.terminar_reposiciones()

# ===== HILO DE REVISIÓN: CONTROL DE INVENTARIO =====

def revisar(num_revisor):
    catalogo = gestor.obtener_catalogo()

    # Usamos el mismo reparto que el de las cajas
    for prox_producto in range(num_revisor-1, len(catalogo), D.NUM_REVISORES):
        producto, _ = catalogo[prox_producto] # prox_producto es numero de iteracion del range, los otros 2 no se van cambiando, solo se cambia el prox_producto, por lo tanto esto sería tal que producto1, producto2, producto3, producto4, producto5, producto6, producto7, producto8, producto9, producto10
        stock = gestor.registrar_revision(producto)
        print(f"Revisor {num_revisor} comprobando el producto: {producto} --> {stock} unidades.\n")
    print(f"El revisor {num_revisor} ha terminado y esta esperando en la barrera.\n")
    barrera.wait() # Le indicamos que se quede aqui hasta que llegan todos los demás.



# ===== PROGRAMA PRINCIPAL =====

if __name__ == "__main__":

    # ===== CREACIÓN DE HILOS DE CAJA Y ALMACÉN =====

    paquete_hilos = []

    for y in range(D.NUM_CAJAS):
        # Definimos el hilo
        hilos = threading.Thread(target=vender, args=(y+1,))
        paquete_hilos.append(hilos)

    # Creamos el hilo de almacen
    hilo_almacen = threading.Thread(target=reponer)


    # ===== INICIO DE HILOS DE VENTA Y REPOSICIÓN =====

    for i in paquete_hilos:
        i.start() #Iniciamos todos los hilos
   
    hilo_almacen.start() # Iniciamos el almacen


    # ===== ESPERA A LA FINALIZACIÓN DE VENTAS Y REPOSICIONES =====

    for z in paquete_hilos:
        z.join()
    
    hilo_almacen.join() # Esperamos a que termine el almacen


    # ===== CREACIÓN E INICIO DE HILOS REVISORES =====

    paquete_revisados = []
    for e in range(D.NUM_REVISORES):
        revisor = threading.Thread(target=revisar, args=(e+1, ))
        paquete_revisados.append(revisor)

    for revisor in paquete_revisados:
        revisor.start()


    # ===== SINCRONIZACIÓN DE REVISORES =====

    barrera.wait() # El cierre no continua hasta que todos los revisores lleguen a la barrera.


    # ===== RESUMEN FINAL DEL INVENTARIO =====

    # Solo llegamos aqui cuando se supera la barrera
    print("\n===== RESUMEN =====\n"
          f"INVENTARIO FINAL --> {gestor.estanteria}\n"
          f"Productos agotados --> {gestor.productos_agotados if gestor.productos_agotados else 'Ninguno'}\n"
          f"Producto en negativos --> {gestor.productos_negativos if gestor.productos_negativos else 'Ninguno'}\n"
          f"TOTAL DE UNIDADES EN EL ALMACEN --> {gestor.unidades_totales()}") # Modificacion

    # ===== RESUMEN DE ESTADÍSTICAS DE VENTAS =====

    # Modificación 
    # Estadisticas de ventas
    vendidos, rechazados, total = gestor.estadisticas_ventas()
    print(f"\n======== ESTADISTICAS DE VENTAS ========\n"f"Pedidos vendidos --> {vendidos}\n"f"Pedidos rechazados --> {rechazados}\n"f"Total de pedidos procesados --> {total}\n")



    # ===== CIERRE DE HILOS Y VALIDACIÓN FINAL =====

    for revisor in paquete_revisados:
        revisor.join()
    assert not gestor.productos_negativos # Verificamos que no hay productos en negativo dentro del inventario