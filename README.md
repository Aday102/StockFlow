# StockFlow
## Descripción general del proyecto
El proyecto que hemos desarrollado se realizaba mediante hilos, el objetivo a cumplir de este proyecto era ser capaces de comprender y detectar los distintos problemas que nos pueden ocasionar los hilos(condicion de carrera, sección crítica) y a como ser capaces de preverlos para poder remediarlos con los metodos de la librería(Lock, RLock, Semaphore, Condition, Barrier).

El proyecto estaba contextualizado en la simulacion de una tienda en la que varias cajas procesan pedidos al mismo tiempo.

## Estructura
```
C:.
└───StockFlow
        .gitignore
        datos.py
        practica_stockflow_actualizada.pdf
        README.md
        StockFlow.py
```
## Sección critica del programa
La sección critica del programa sucede cuando 2 hilos están accediendo a un mismo recurso compartido y que no deberia estar siendo ejecutado por varios hilos al mismo tiempo.

## Uso y finalidad del Lock, RLock, Semaphore, Condition y Barrier

- Lock → Sirve para evitar que 2 hilos modifiquen el mismo dato a la vez, es decir su finalidad es evitar que se produzca la condición de carrera.

- RLock → Cuando varias funciones llaman a un mismo Lock normal esto lo que hace es que un hilo se espere asi mismo para siempre.

- Semaphore → Limita cuantos hilos pueden hacer una misma cosa a la vez, es decir, coloca un maximo de hilos. 

- Condition → Sirve para que un hilo se quede esperando a que se cumpla algo sin gastar CPU.

- Barrier → Sincroniza los hilos por fases, si todos los hilos tienen que terminar en la fase 1, se esperan y una vez estén todos terminados empiezan juntos la fase 2.


## ¿Por que RLock es necesario en la fase 6?(Refactorización con RLock)
Era nec
