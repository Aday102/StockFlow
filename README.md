# StockFlow

## Uso y finalidad del Lock, RLock, Semaphore, Condition y Barrier

- Lock → Sirve para evitar que 2 hilos modifiquen el mismo dato a la vez, es decir su finalidad es evitar que se produzca la condición de carrera.

- RLock → Cuando varias funciones llaman a un mismo Lock normal esto lo que hace es que un hilo se espere asi mismo para siempre.

- Semaphore → Limita cuantos hilos pueden hacer una misma cosa a la vez, es decir, coloca un maximo de hilos. 

- Condition → Sirve para que un hilo se quede esperando a que se cumpla algo sin gastar CPU.

- Barrier → Sincroniza los hilos por fases, si todos los hilos tienen que terminar en la fase 1, se esperan y una vez estén todos terminados empiezan juntos la fase 2.
## Sección critica del programa
La sección critica del programa sucede cuando 2 hilos están accediendo a un mismo recurso compartido y que no deberia estar siendo ejecutado por varios hilos al mismo tiempo.


## FASE 6: ¿Por que es necesario LRock() en este diseño?
La gestión del inventario esta dentro del  inventario de la clase y todas sus operaciones estan protegidas con la misma cerradura. Algunas de esas operaciones, llaman a otras del mismo gestor, lo que significa que con un lock normal se hubiera provocado un interbloqueo, es decir el hilo ya cuenta con una cerradura y al intentar cogerla de nueva, se queda esperando a que se libere, cuando en realidad se tiene que liberar el mismo. 

Por eso Rlock es necesario, este recuerda que hilos tiene ya la cerrradura y cuantas veces la ha cogido.
