# StockFlow

## Uso y finalidad del Lock, RLock, Semaphore, Condition y Barrier

- Lock → Sirve para evitar que 2 hilos modifiquen el mismo dato a la vez, es decir su finalidad es evitar que se produzca la condición de carrera.

- RLock → Cuando varias funciones llaman a un mismo Lock normal esto lo que hace es que un hilo se espere asi mismo para siempre.

- Semaphore → Limita cuantos hilos pueden hacer una misma cosa a la vez, es decir, coloca un maximo de hilos. 

- Condition → Sirve para que un hilo se quede esperando a que se cumpla algo sin gastar CPU.

- Barrier → Sincroniza los hilos por fases, si todos los hilos tienen que terminar en la fase 1, se esperan y una vez estén todos terminados empiezan juntos la fase 2.
