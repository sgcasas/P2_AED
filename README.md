# Anima tu Algoritmo: BFS 0-1

Proyecto Final 2 de CS2023 Algoritmos y Estructuras de Datos (UTEC, 2026-2).

BFS 0-1 calcula los caminos mínimos desde un nodo origen hacia todos los demás en un grafo dirigido cuyas aristas pesan 0 o 1, en O(|V| + |E|). Usa una deque: los nodos alcanzados por una arista de peso 0 entran por adelante y los de peso 1 por atrás.

El programa en C++ ejecuta el algoritmo y guarda cada paso en un JSON. La animación lee ese JSON, así que todo lo que se ve en el video sale de la ejecución real.

## Software requerido

- g++ con soporte para C++17
- (Animación) ver la carpeta `animation/`

## Compilar

```bash
g++ -std=c++17 -O2 src/bfs01.cpp -o bfs01
```

## Ejecutar

```bash
./bfs01 inputs/ejemplo.txt > steps/ejemplo.json
./bfs01 inputs/borde.txt   > steps/borde.json
```

### Formato de entrada

```
n m s        # cantidad de nodos, cantidad de aristas, nodo origen
u v w        # m líneas: arista dirigida u -> v con peso w (0 o 1)
```

Los nodos van de `0` a `n-1`.

### Formato de salida (JSON)

```json
{
  "graph": {"n": 7, "source": 0, "edges": [{"u":0,"v":2,"w":1}, ...]},
  "steps": [
    {"type":"init", "node":0, "deque":[0], "dist":[0,null,...], "parent":[-1,...]},
    ...
  ]
}
```

Cada paso trae una copia de `deque`, `dist` y `parent` (`null` = ∞, `-1` = sin padre). Tipos de paso:

| type         | significado                                                         | campos extra                     |
|--------------|---------------------------------------------------------------------|----------------------------------|
| `init`       | el origen entra a la deque con distancia 0                          | `node`                           |
| `pop`        | se saca un nodo del frente y se procesan sus aristas                | `node`                           |
| `relax`      | una arista mejora la distancia de su destino                        | `edge`, `old`, `new`, `push` (`front`/`back`) |
| `no_improve` | una arista no mejora la distancia                                    | `edge`                           |
| `stale`      | sale un nodo que ya fue procesado (entrada vieja) y se salta        | `node`                           |
| `done`       | la deque quedó vacía: distancias finales                            | —                                |

## Instancias

- `inputs/ejemplo.txt`: 7 nodos. El nodo 2 se descubre primero con distancia 1 (arista 0→2) y luego baja a 0 por el camino 0→1→2 de aristas de peso 0. Ahí se ve por qué hay que meter por adelante y aparece un paso `stale`.
- `inputs/borde.txt` (caso borde): un ciclo de aristas de peso 0 (0→1→2→0) y un nodo inalcanzable (4), que termina con distancia ∞.

## Implementación

- `src/bfs01.cpp` implementa el algoritmo y su propia deque con buffer circular; no usa `std::deque` ni ninguna librería de grafos.
- La deque tiene capacidad `m + 2`: cada inserción viene de una relajación exitosa y cada arista se relaja a lo más una vez con éxito (su nodo de salida se procesa una sola vez).

## Complejidad

- Tiempo: O(|V| + |E|). Cada nodo se procesa una vez (las salidas repetidas se saltan en O(1)) y cada arista se revisa una vez. Le gana a Dijkstra, que es O((|V| + |E|) log |V|).
- Memoria: O(|V| + |E|).
