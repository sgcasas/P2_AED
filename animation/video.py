import json
from pathlib import Path
from manim import *

STEPS = Path(__file__).resolve().parent.parent / "steps"

def cargar(nombre):
    with open(STEPS / f"{nombre}.json", encoding="utf-8") as f:
        return json.load(f)

# ---------- Datos del proyecto ----------
TITULO = "BFS 0-1"
SUBTITULO = "Caminos mínimos en grafos con pesos 0 y 1"
CURSO = "CS2023 - Algoritmos y Estructuras de Datos  ·  UTEC 2026-2"
INTEGRANTES = [
    "Sebastian Casas Matos",
    "Enzo Calderon Soto",
    "Valentino Infante Garcia",
]
# Posiciones en pantalla (solo diseño visual): nodo -> (x, y, dónde va su dist)
POS = {
    "ejemplo": {0: (-5.6, 0.0, DOWN), 1: (-4.2, 1.5, UP), 2: (-4.2, -1.5, DOWN),
                3: (-2.6, 1.5, UP), 4: (-2.6, -0.3, DOWN), 5: (-1.0, 0.6, UP),
                6: (-1.0, -1.8, DOWN)},
    "borde":   {0: (-5.2, 1.2, UP), 1: (-2.8, 1.2, UP), 2: (-4.0, -0.6, DOWN),
                3: (-1.8, -1.6, DOWN), 4: (-5.4, -1.8, UP)},
}
COLOR_ACTUAL = PINK
COLOR_PROCESADO = BLUE_E

class VideoBFS01(Scene):
    def construct(self):
        self.seccion_titulo()
        self.seccion_intro()
        self.seccion_ejecucion()
        self.seccion_borde()
        self.seccion_complejidad()
        self.seccion_creditos()

    def limpiar(self):
        self.play(FadeOut(*self.mobjects))

    # ---------- 1. Título ----------
    def seccion_titulo(self):
        t = Text(TITULO, font_size=80, weight=BOLD)
        sub = Text(SUBTITULO, font_size=32, color=GRAY_B).next_to(t, DOWN)
        nombres = VGroup(*[Text(n, font_size=26) for n in INTEGRANTES])
        nombres.arrange(DOWN, buff=0.15).next_to(sub, DOWN, buff=0.8)
        curso = Text(CURSO, font_size=22, color=GRAY).to_edge(DOWN)

        self.play(Write(t))
        self.play(FadeIn(sub, shift=0.2 * UP))
        self.play(LaggedStart(*[FadeIn(n) for n in nombres], lag_ratio=0.3),
                  FadeIn(curso))
        self.wait(2)
        self.limpiar()

        # ---------- utilidades ----------
    def caja(self, texto, color=BLUE):
        r = Square(side_length=0.9, color=color, fill_opacity=0.25)
        t = Text(texto, font_size=26).move_to(r)
        return VGroup(r, t)

    def acomodar(self, elems, izq, der, centro):
        """Devuelve animaciones para alinear las cajas en fila y mover las etiquetas."""
        obj = VGroup(*[m.copy() for m in elems]).arrange(RIGHT, buff=0).move_to(centro)
        anims = [m.animate.move_to(o) for m, o in zip(elems, obj)]
        anims += [izq.animate.next_to(obj, LEFT), der.animate.next_to(obj, RIGHT)]
        return anims

    # ---------- 2. Intro conceptual ----------
    def seccion_intro(self):
        titulo = Text("¿Qué es BFS 0-1?", font_size=44, weight=BOLD).to_edge(UP)
        puntos = VGroup(
            Text("• Calcula caminos mínimos desde un origen a todos los nodos", font_size=26),
            Text("• En grafos dirigidos cuyas aristas pesan 0 o 1", font_size=26),
            Text("• Uso: laberintos con movimientos gratis, mínimo de aristas a invertir", font_size=26),
            Text("• Más rápido que Dijkstra: no necesita cola de prioridad", font_size=26),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.35).next_to(titulo, DOWN, buff=0.7)

        self.play(Write(titulo))
        for p in puntos:
            self.play(FadeIn(p, shift=0.2 * RIGHT), run_time=0.8)
            self.wait(0.7)
        self.wait(1)
        self.play(FadeOut(puntos))

        # Idea clave: la deque
        idea = Text("Idea: una deque (cola doble) en lugar de una cola",
                    font_size=30).next_to(titulo, DOWN, buff=0.5)
        self.play(Write(idea))

        centro = DOWN * 0.8
        cajas = [self.caja(t) for t in ["d", "d", "d+1", "d+1"]]
        VGroup(*cajas).arrange(RIGHT, buff=0).move_to(centro)
        frente = Text("frente", font_size=22, color=GRAY).next_to(VGroup(*cajas), LEFT)
        final = Text("final", font_size=22, color=GRAY).next_to(VGroup(*cajas), RIGHT)
        self.play(*[Create(c) for c in cajas], FadeIn(frente, final))

        # Peso 0 -> entra por el frente
        n0 = self.caja("d", GREEN).move_to(cajas[0]).shift(1.4 * UP)
        t0 = Text("arista de peso 0 → entra por el FRENTE", font_size=24,
                  color=GREEN).next_to(VGroup(*cajas), DOWN, buff=0.8)
        self.play(FadeIn(n0), Write(t0))
        cajas = [n0] + cajas
        self.play(*self.acomodar(cajas, frente, final, centro))
        self.wait(0.8)

        # Peso 1 -> entra por el final
        n1 = self.caja("d+1", ORANGE).move_to(cajas[-1]).shift(1.4 * UP)
        t1 = Text("arista de peso 1 → entra por el FINAL", font_size=24,
                  color=ORANGE).move_to(t0)
        self.play(FadeIn(n1), ReplacementTransform(t0, t1))
        cajas = cajas + [n1]
        self.play(*self.acomodar(cajas, frente, final, centro))
        self.wait(0.8)

        conclusion = Text("La deque queda ordenada por distancia:\n"
                          "siempre sacamos del frente el nodo más cercano",
                          font_size=26, color=YELLOW).move_to(t1)
        self.play(ReplacementTransform(t1, conclusion))
        self.wait(2.5)
        self.limpiar()
        # ---------- herramientas para la ejecución ----------
    def construir_grafo(self, g, pos):
        nodos = {}
        for v in range(g["n"]):
            x, y, _ = pos[v]
            c = Circle(radius=0.35, color=WHITE, stroke_width=3,
                       fill_color=BLACK, fill_opacity=1).move_to([x, y, 0])
            t = Text(str(v), font_size=26).move_to(c)
            nodos[v] = VGroup(c, t)

        aristas, pesos = {}, []
        for e in g["edges"]:
            a = nodos[e["u"]][0].get_center()
            b = nodos[e["v"]][0].get_center()
            flecha = Arrow(a, b, buff=0.38, stroke_width=3, tip_length=0.2,
                           color=GRAY_D)
            d = (b - a) / np.linalg.norm(b - a)
            normal = np.array([-d[1], d[0], 0])
            w = Text(str(e["w"]), font_size=20,
                     color=GREEN if e["w"] == 0 else ORANGE)
            w.move_to(flecha.get_center() + 0.22 * normal)
            aristas[(e["u"], e["v"], e["w"])] = flecha
            pesos.append(w)
        return nodos, aristas, pesos

    def etiqueta_dist(self, val, nodo, direc):
        return Text(val, font_size=22, color=YELLOW).next_to(nodo, direc, buff=0.08)

    def dibujar_deque(self, items, ancla):
        if not items:
            m = Text("vacía", font_size=22, color=GRAY)
        else:
            m = VGroup(*[self.caja(str(x)) for x in items]).arrange(RIGHT, buff=0).scale(0.7)
        return m.next_to(ancla, RIGHT, buff=0.25)

    def describir(self, p):
        t = p["type"]
        if t == "init":
            return f"Inicio: dist[{p['node']}] = 0 y {p['node']} entra a la deque"
        if t == "pop":
            return f"Sacamos {p['node']} del frente y revisamos sus aristas"
        if t == "stale":
            return f"Sale {p['node']} otra vez, pero ya fue procesado: se ignora"
        if t == "done":
            return "Deque vacía: estas son las distancias mínimas finales"
        e = p["edge"]
        u, v, w = e["u"], e["v"], e["w"]
        if t == "relax":
            old = "∞" if p["old"] is None else p["old"]
            lado = "FRENTE" if p["push"] == "front" else "FINAL"
            return f"{u}→{v} (peso {w}): dist[{v}] {old} → {p['new']}, entra por el {lado}"
        du, dv = p["dist"][u], p["dist"][v]
        return f"{u}→{v} (peso {w}): {du} + {w} = {du + w} no mejora dist[{v}] = {dv}"

    def animar_ejecucion(self, nombre, titulo_txt, vel=1.0, limpiar_al_final=True):
        data = cargar(nombre)
        g, pasos = data["graph"], data["steps"]
        pos = POS[nombre]

        titulo = Text(titulo_txt, font_size=34, weight=BOLD).to_edge(UP)
        nodos, aristas, pesos = self.construir_grafo(g, pos)

        # Panel derecho: deque + leyenda
        cab = Text("Deque", font_size=28, weight=BOLD).move_to([3.6, 2.2, 0])
        frente = Text("frente", font_size=18, color=GRAY).move_to([1.2, 1.3, 0])
        deque_m = self.dibujar_deque([], frente)
        leyenda = VGroup(
            Text("número amarillo = dist", font_size=18, color=YELLOW),
            Text("borde rosado = nodo actual", font_size=18, color=COLOR_ACTUAL),
            Text("relleno azul = procesado", font_size=18, color=BLUE),
            Text("arista blanca = camino mínimo", font_size=18),
            Text("peso 0 (verde)  /  peso 1 (naranja)", font_size=18, color=GRAY_B),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to([3.6, -1.0, 0])

        dist_val = {v: "∞" for v in range(g["n"])}
        dist_lbl = {v: self.etiqueta_dist("∞", nodos[v], pos[v][2]) for v in range(g["n"])}

        self.play(Write(titulo))
        self.play(*[GrowArrow(a) for a in aristas.values()],
                  *[FadeIn(w) for w in pesos], *[FadeIn(n) for n in nodos.values()])
        self.play(*[FadeIn(l) for l in dist_lbl.values()],
                  FadeIn(cab, frente, deque_m), FadeIn(leyenda))

        caption = Text(" ", font_size=24).to_edge(DOWN)
        contador = Text(" ", font_size=18).to_corner(UR)
        en_arbol = {k: False for k in aristas}
        actual = None

        for i, p in enumerate(pasos):
            t = p["type"]
            color_cap = {"relax": GREEN, "no_improve": RED, "stale": GRAY}.get(t, WHITE)
            anims = []

            nuevo = Text(self.describir(p), font_size=24, color=color_cap).to_edge(DOWN)
            anims.append(ReplacementTransform(caption, nuevo)); caption = nuevo
            nc = Text(f"paso {i + 1}/{len(pasos)}", font_size=18, color=GRAY).to_corner(UR).shift(0.7 * DOWN)
            anims.append(ReplacementTransform(contador, nc)); contador = nc

            nd = self.dibujar_deque(p["deque"], frente)
            anims.append(ReplacementTransform(deque_m, nd)); deque_m = nd

            for v in range(g["n"]):
                val = "∞" if p["dist"][v] is None else str(p["dist"][v])
                if val != dist_val[v]:
                    nl = self.etiqueta_dist(val, nodos[v], pos[v][2])
                    anims.append(ReplacementTransform(dist_lbl[v], nl))
                    dist_lbl[v], dist_val[v] = nl, val

            for (u, v, w), flecha in aristas.items():
                debe = p["parent"][v] == u
                if debe != en_arbol[(u, v, w)]:
                    anims.append(flecha.animate.set_color(WHITE if debe else GRAY_D))
                    en_arbol[(u, v, w)] = debe

            if t == "pop" or t == "done":
                if actual is not None:
                    anims.append(nodos[actual][0].animate.set_stroke(WHITE, width=3))
                if t == "pop":
                    actual = p["node"]
                    anims.append(nodos[actual][0].animate
                                 .set_stroke(COLOR_ACTUAL, width=6)
                                 .set_fill(COLOR_PROCESADO, opacity=1))
                else:
                    actual = None
            elif t == "stale":
                anims.append(Indicate(nodos[p["node"]], color=GRAY))
            elif t in ("relax", "no_improve"):
                e = p["edge"]
                flash = aristas[(e["u"], e["v"], e["w"])].copy()
                flash.set_color(GREEN if t == "relax" else RED).set_stroke(width=8)
                anims.append(ShowPassingFlash(flash, time_width=0.6))

            self.play(*anims, run_time=1.0 * vel)
            self.wait((1.5 if t in ("stale", "done") else 0.6) * vel)

        self.wait(1.5)
        if limpiar_al_final:
            self.limpiar()
        return nodos, data, caption

    # ---------- 3. Ejecución ----------
    def seccion_ejecucion(self):
        self.animar_ejecucion("ejemplo", "Ejecución sobre un grafo de 7 nodos")

        # ---------- 4. Caso borde ----------
    def seccion_borde(self):
        t = Text("Caso borde", font_size=48, weight=BOLD)
        d = VGroup(
            Text("• Un ciclo formado solo por aristas de peso 0", font_size=28),
            Text("• Un nodo al que no se puede llegar desde el origen", font_size=28),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).next_to(t, DOWN, buff=0.6)
        self.play(Write(t))
        self.play(FadeIn(d, shift=0.2 * UP))
        self.wait(2.5)
        self.limpiar()

        nodos, data, caption = self.animar_ejecucion(
            "borde", "Caso borde: ciclo de peso 0 y nodo inalcanzable",
            vel=0.8, limpiar_al_final=False)

        # Nodos inalcanzables: los que terminan con dist = null en el JSON
        final = data["steps"][-1]["dist"]
        inalc = [str(v) for v, dv in enumerate(final) if dv is None]

        nota = VGroup(
            Text("Ciclo de peso 0: cada nodo se procesa una sola vez, no hay bucle infinito",
                 font_size=22, color=GREEN),
            Text(f"Nodo {', '.join(inalc)} inalcanzable: su distancia queda en ∞",
                 font_size=22, color=RED),
        ).arrange(DOWN, buff=0.12).to_edge(DOWN)

        self.play(ReplacementTransform(caption, nota),
                  *[Circumscribe(nodos[int(v)], color=RED) for v in inalc])
        self.wait(3)
        self.limpiar()

        # ---------- 5. Complejidad ----------
    def seccion_complejidad(self):
        data = cargar("ejemplo")
        pasos = data["steps"]
        n, m = data["graph"]["n"], len(data["graph"]["edges"])
        pops = sum(p["type"] == "pop" for p in pasos)
        revisadas = sum(p["type"] in ("relax", "no_improve") for p in pasos)
        stale = sum(p["type"] == "stale" for p in pasos)

        titulo = Text("Complejidad", font_size=44, weight=BOLD).to_edge(UP)
        puntos = VGroup(
            Text("• Cada nodo se procesa una sola vez  →  O(|V|)", font_size=26),
            Text("• Cada arista se revisa una sola vez  →  O(|E|)", font_size=26),
            Text("• push_front, push_back y pop_front de la deque  →  O(1)", font_size=26),
            Text("• Las entradas repetidas (stale) se descartan en O(1)", font_size=26),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).next_to(titulo, DOWN, buff=0.5)

        ejemplo = Text(f"En el ejemplo (|V| = {n}, |E| = {m}): {pops} nodos procesados, "
                       f"{revisadas} aristas revisadas, entradas descartadas: {stale}",
                       font_size=20, color=GRAY_B)
        res = Text("Tiempo: O(|V| + |E|)      Memoria: O(|V| + |E|)", font_size=32, color=YELLOW)
        marco = SurroundingRectangle(res, color=YELLOW, buff=0.25)
        comp = VGroup(
            Text("Dijkstra con heap:  O((|V| + |E|) log |V|)", font_size=24, color=GRAY_B),
            Text("BFS 0-1:  O(|V| + |E|)  →  sin el factor log", font_size=24, color=GREEN),
        ).arrange(DOWN, buff=0.15)
        VGroup(ejemplo, VGroup(res, marco), comp).arrange(DOWN, buff=0.45).next_to(puntos, DOWN, buff=0.5)

        self.play(Write(titulo))
        self.play(LaggedStart(*[FadeIn(p, shift=0.2 * RIGHT) for p in puntos], lag_ratio=0.5),
                  run_time=3)
        self.play(FadeIn(ejemplo))
        self.play(Create(marco), Write(res))
        self.play(FadeIn(comp, shift=0.2 * UP))
        self.wait(3)
        self.limpiar()

    # ---------- 6. Créditos ----------
    def seccion_creditos(self):
        gracias = Text("¡Gracias!", font_size=60, weight=BOLD)
        nombres = VGroup(*[Text(n, font_size=26) for n in INTEGRANTES]).arrange(DOWN, buff=0.15)
        info = VGroup(
            Text(CURSO, font_size=22, color=GRAY),
            Text("Implementación: C++17 con deque propia  ·  Animación: Python + Manim Community",
                 font_size=20, color=GRAY),
            Text("Estilo inspirado en 3Blue1Brown", font_size=20, color=GRAY),
        ).arrange(DOWN, buff=0.12)
        VGroup(gracias, nombres, info).arrange(DOWN, buff=0.6)

        self.play(Write(gracias))
        self.play(FadeIn(nombres, shift=0.2 * UP))
        self.play(FadeIn(info))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))