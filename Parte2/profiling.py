#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lab 7 - Parte 2: profiling de los algoritmos a, b y c.
    python3 profiling.py
"""

import shutil
import subprocess
from pathlib import Path

AQUI = Path(__file__).resolve().parent
BINARIO = AQUI / "algoritmos"
TAMANOS = [1, 10, 100, 1000, 10000, 100000, 1000000]


# Formulas  de la Parte 1 (conteo de operaciones)

def T_a(n):
    m = n - n // 2              # iteraciones del ciclo de j = ceil(n/2)
    L = n.bit_length() - 1      # floor(log2 n)
    return 1 + (m + 2) + (m + 1) ** 2 + (m + 1) * m * (L + 2) + (m + 1) * m * (L + 1)


def T_b(n):
    return 1 if n <= 1 else 4 * n + 3


def T_c(n):
    p = n // 3                  # iteraciones del ciclo de i = floor(n/3)
    q = (n + 3) // 4            # iteraciones del ciclo de j = ceil(n/4)
    return 2 * p * q + 2 * p + 2


FORMULAS = {"a": T_a, "b": T_b, "c": T_c}


# Compilacion y corridas

def compilar():
    subprocess.run(["cc", "-O0", "-o", str(BINARIO), str(AQUI / "algoritmos.c")], check=True)


def repeticiones(n):
    """Para n chicos una sola corrida dura nanosegundos; se repite y se promedia."""
    if n <= 10:
        return 100000
    if n <= 100:
        return 1000
    if n <= 1000:
        return 10
    return 1


def medir_tiempo(alg, n):
    r = subprocess.run([str(BINARIO), "tiempo", alg, str(n), str(repeticiones(n))],
                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, check=True)
    return float(r.stderr.strip())


def contar_instrumentado(alg, n):
    r = subprocess.run([str(BINARIO), "conteo", alg, str(n)],
                       capture_output=True, text=True, check=True)
    return int(r.stdout.strip())


def perfilar(alg):
    filas = []
    for n in TAMANOS:
        t = medir_tiempo(alg, n)
        ops = contar_instrumentado(alg, n)
        if ops != FORMULAS[alg](n):
            raise RuntimeError(f"{alg}, n={n}: instrumentado={ops} pero formula={FORMULAS[alg](n)}")
        filas.append({"n": n, "tiempo": t, "ops": ops})
        print(f"  {alg}  n={n:>7}  {t:.6g} s  ops={ops:,}")
    return filas


# Tabla

def fmt_tiempo(t):
    if t >= 60:
        return f"{t:,.1f} s (~{t / 60:,.1f} min)"
    return f"{t:.3e} s"


def tabla_md(alg, filas):
    lineas = [f"## Algoritmo {alg}", "",
              "| n | Tiempo real | Operaciones contadas | ns por operacion |",
              "|---:|---:|---:|---:|"]
    for f in filas:
        ns = f["tiempo"] / f["ops"] * 1e9
        lineas.append(f"| {f['n']:,} | {fmt_tiempo(f['tiempo'])} | {f['ops']:,} | {ns:.2f} |")
    return "\n".join(lineas)


def grafica_png(alg, filas, ruta_png):
    import math

    W, H = 860, 520
    izq, der, arr, aba = 90, 100, 60, 70
    ancho, alto = W - izq - der, H - arr - aba

    MARGEN = 0.4   

    def x_de(n):
        return izq + (math.log10(n) + MARGEN) / (6 + 2 * MARGEN) * ancho

    def rango_log(valores):
        lo = math.floor(math.log10(min(valores)))
        hi = math.ceil(math.log10(max(valores)))
        return lo, max(hi, lo + 1)

    tiempos = [max(f["tiempo"], 1e-12) for f in filas]
    opss = [f["ops"] for f in filas]
    t_lo, t_hi = rango_log(tiempos)
    o_lo, o_hi = rango_log(opss)

    def y_de(v, lo, hi):
        return arr + alto - (math.log10(v) - lo + MARGEN) / (hi - lo + 2 * MARGEN) * alto

    AZUL, NARANJA, GRIS = "#2f5fb0", "#c9731e", "#9aa0a6"
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'font-family="Helvetica, Arial, sans-serif" font-size="12">',
         f'<rect width="{W}" height="{H}" fill="white"/>',
         f'<text x="{W / 2}" y="30" text-anchor="middle" font-size="16" font-weight="bold">'
         f'Algoritmo {alg}: tiempo real vs. conteo de operaciones</text>']

    # rejilla y ejes
    for k in range(0, 7):
        x = x_de(10 ** k)
        s.append(f'<line x1="{x}" y1="{arr}" x2="{x}" y2="{arr + alto}" stroke="#e5e7eb"/>')
        s.append(f'<text x="{x}" y="{arr + alto + 18}" text-anchor="middle">10^{k}</text>')
    for e in range(t_lo, t_hi + 1):
        y = y_de(10 ** e, t_lo, t_hi)
        s.append(f'<line x1="{izq}" y1="{y}" x2="{izq + ancho}" y2="{y}" stroke="#e5e7eb"/>')
        s.append(f'<text x="{izq - 8}" y="{y + 4}" text-anchor="end" fill="{AZUL}">1e{e}</text>')
    for e in range(o_lo, o_hi + 1):
        y = y_de(10 ** e, o_lo, o_hi)
        s.append(f'<text x="{izq + ancho + 8}" y="{y + 4}" fill="{NARANJA}">1e{e}</text>')
    s.append(f'<rect x="{izq}" y="{arr}" width="{ancho}" height="{alto}" fill="none" stroke="#374151"/>')
    s.append(f'<text x="{izq + ancho / 2}" y="{H - 25}" text-anchor="middle">n (tamaño de entrada, escala log)</text>')
    s.append(f'<text transform="translate(25,{arr + alto / 2}) rotate(-90)" text-anchor="middle" '
             f'fill="{AZUL}">Tiempo real (segundos, escala log)</text>')
    s.append(f'<text transform="translate({W - 20},{arr + alto / 2}) rotate(90)" text-anchor="middle" '
             f'fill="{NARANJA}">Operaciones contadas (escala log)</text>')

    # serie de tiempo real
    ptst = [(x_de(f["n"]), y_de(max(f["tiempo"], 1e-12), t_lo, t_hi)) for f in filas]
    s.append('<polyline fill="none" stroke="%s" stroke-width="2" points="%s"/>'
             % (AZUL, " ".join(f"{x:.1f},{y:.1f}" for x, y in ptst)))
    for x, y in ptst:
        s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{AZUL}" stroke="{AZUL}" stroke-width="2"/>')

    # serie de operaciones (encima, cuadros mas chicos, para que no queden tapados por los circulos)
    pts = [(x_de(f["n"]), y_de(f["ops"], o_lo, o_hi)) for f in filas]
    s.append('<polyline fill="none" stroke="%s" stroke-width="2" points="%s"/>'
             % (NARANJA, " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)))
    for x, y in pts:
        s.append(f'<rect x="{x - 3.5:.1f}" y="{y - 3.5:.1f}" width="7" height="7" fill="{NARANJA}" '
                 f'stroke="white" stroke-width="1"/>')

    # leyenda
    lx, ly = izq + 12, arr + 12
    s.append(f'<rect x="{lx - 6}" y="{ly - 6}" width="200" height="52" fill="white" stroke="{GRIS}"/>')
    s.append(f'<circle cx="{lx + 8}" cy="{ly + 8}" r="5" fill="{AZUL}"/>'
             f'<text x="{lx + 22}" y="{ly + 12}">Tiempo real medido</text>')
    s.append(f'<rect x="{lx + 4}" y="{ly + 24}" width="8" height="8" fill="{NARANJA}"/>'
             f'<text x="{lx + 22}" y="{ly + 32}">Operaciones contadas</text>')

    s.append("</svg>")
    svg = "\n".join(s)

    if shutil.which("rsvg-convert"):
        subprocess.run(["rsvg-convert", "-o", str(ruta_png)], input=svg.encode("utf-8"), check=True)
    else:
        print(f"  (rsvg-convert no esta instalado; no se genero {ruta_png.name})")


def main():
    compilar()
    (AQUI / "graficas").mkdir(exist_ok=True)

    secciones = ["# Resultados del profiling (Parte 2)", ""]
    for alg in ("a", "b", "c"):
        print(f"Algoritmo {alg}:")
        filas = perfilar(alg)
        secciones += [tabla_md(alg, filas), "", ""]
        grafica_png(alg, filas, AQUI / "graficas" / f"algoritmo_{alg}.png")

    (AQUI / "resultados.md").write_text("\n".join(secciones), encoding="utf-8")
    print("\nTabla: resultados.md   Graficas: graficas/")


if __name__ == "__main__":
    main()
