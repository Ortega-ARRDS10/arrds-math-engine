"""Banco de verificación: fuente única de verdad del motor.

Cada caso invoca una operación **a través de la API** (así se valida
también el contrato JSON) y compara contra un valor de referencia
analítico o tabulado, con tolerancia propia. Los casos son datos puros
(JSON), de modo que cualquier otra implementación del motor puede
correrlos igual::

    python -m arrds_math.selftest              # corre todo y muestra la tabla
    python -m arrds_math.selftest --module units
    python -m arrds_math.selftest --export casos.json

Campos de un caso:

* ``id``, ``operation``, ``params``, ``reference`` (de dónde sale el valor).
* ``path``: ruta dentro de ``result`` (``"value"``, ``"value.values.0"``...).
* ``expected`` + ``tol`` (absoluta; ``rel: true`` la vuelve relativa).
* o bien ``expect_error``: el ``code`` de error esperado.
* ``check_error_estimate``: además exige que |obtenido − esperado| ≤
  error_estimate·10 + tol (el error reportado no debe mentir).
"""

import json
import math
import sys

from .api import run

PI = math.pi

CASES = [
    # --- expr (Capa 1) -------------------------------------------------
    {"id": "expr.eval.pitagoras", "operation": "expr.evaluate",
     "params": {"expression": "sqrt(x^2 + y^2)", "variables": {"x": 3, "y": 4}},
     "path": "value", "expected": 5.0, "tol": 1e-15, "reference": "terna pitagórica 3-4-5"},
    {"id": "expr.eval.precedencia", "operation": "expr.evaluate", "params": {"expression": "-2^2"},
     "path": "value", "expected": -4.0, "tol": 0, "reference": "la potencia liga más que el signo"},
    {"id": "expr.eval.implicita", "operation": "expr.evaluate",
     "params": {"expression": "2x(x+1)", "variables": {"x": 3}},
     "path": "value", "expected": 24.0, "tol": 0, "reference": "2·3·4"},
    {"id": "expr.eval.factorial", "operation": "expr.evaluate", "params": {"expression": "5! + 0!"},
     "path": "value", "expected": 121.0, "tol": 0, "reference": "120 + 1"},
    {"id": "expr.eval.euler", "operation": "expr.evaluate",
     "params": {"expression": "exp(j*pi) + 1", "complex_mode": True},
     "path": "value", "expected": 0.0, "tol": 1e-15, "reference": "identidad de Euler e^{iπ} + 1 = 0"},
    {"id": "expr.eval.ln_negativo_complejo", "operation": "expr.evaluate",
     "params": {"expression": "ln(-1)", "complex_mode": True},
     "path": "value", "expected": {"re": 0.0, "im": PI}, "tol": 1e-15, "reference": "ln(−1) = iπ (rama principal)"},
    {"id": "expr.derivada.producto", "operation": "expr.derivative",
     "params": {"expression": "x^2*sin(x)", "var": "x"}, "path": "expression",
     "expected": "2 * x * sin(x) + x^2 * cos(x)", "reference": "regla del producto"},
    {"id": "expr.derivada.segunda", "operation": "expr.derivative",
     "params": {"expression": "exp(2x)", "var": "x", "order": 2}, "path": "expression",
     "expected": "4 * exp(2 * x)", "reference": "d²/dx² e^{2x} = 4e^{2x}"},
    {"id": "expr.latex.fraccion", "operation": "expr.to_latex", "params": {"expression": "sqrt(x)/2"},
     "path": "latex", "expected": r"\frac{\sqrt{x}}{2}", "reference": "formato LaTeX"},
    {"id": "expr.simplify.neutros", "operation": "expr.simplify",
     "params": {"expression": "0*x + 1*y + (x^2)^3"}, "path": "expression",
     "expected": "y + x^6", "reference": "identidades x·0, 1·y, (x²)³"},

    # --- numeric (Capa 2) ----------------------------------------------
    {"id": "numeric.integral.seno", "operation": "numeric.simpson_adaptive",
     "params": {"expression": "sin(x)", "a": 0, "b": "pi"},
     "path": "value", "expected": 2.0, "tol": 1e-9, "check_error_estimate": True, "reference": "∫₀^π sin x dx = 2"},
    {"id": "numeric.integral.gauss", "operation": "numeric.gauss_legendre",
     "params": {"expression": "exp(-x^2)", "a": -6, "b": 6, "n": 60},
     "path": "value", "expected": math.sqrt(PI), "tol": 1e-12, "reference": "∫ e^{−x²} = √π"},
    {"id": "numeric.integral.arctan", "operation": "numeric.integrate",
     "params": {"expression": "4/(1+x^2)", "a": 0, "b": 1},
     "path": "value", "expected": PI, "tol": 1e-9, "check_error_estimate": True, "reference": "∫₀¹ 4/(1+x²) = π"},
    {"id": "numeric.trapecio.lineal", "operation": "numeric.trapezoid",
     "params": {"y": [0, 1, 2, 3], "dx": 1}, "path": "value", "expected": 4.5, "tol": 1e-15,
     "reference": "exacto para funciones lineales"},
    {"id": "numeric.raiz.brent", "operation": "numeric.brent",
     "params": {"expression": "x^3 - 2x - 5", "a": 2, "b": 3},
     "path": "value", "expected": 2.0945514815423265, "tol": 1e-12, "check_error_estimate": True,
     "reference": "raíz clásica de Wallis (x³ − 2x − 5)"},
    {"id": "numeric.raiz.newton", "operation": "numeric.newton",
     "params": {"expression": "x^3 - 2x - 5", "x0": 2},
     "path": "value", "expected": 2.0945514815423265, "tol": 1e-12, "check_error_estimate": True,
     "reference": "raíz clásica de Wallis"},
    {"id": "numeric.raiz.biseccion", "operation": "numeric.bisection",
     "params": {"expression": "x^2 - 2", "a": 0, "b": 2},
     "path": "value", "expected": math.sqrt(2), "tol": 1e-11, "check_error_estimate": True, "reference": "√2"},
    {"id": "numeric.raiz.secante", "operation": "numeric.secant",
     "params": {"expression": "cos(x) - x", "x0": 0, "x1": 1},
     "path": "value", "expected": 0.7390851332151607, "tol": 1e-12, "reference": "número de Dottie"},
    {"id": "numeric.derivada.richardson", "operation": "numeric.derivative",
     "params": {"expression": "exp(x)", "x": 1},
     "path": "value", "expected": math.e, "tol": 1e-9, "check_error_estimate": True, "reference": "d/dx eˣ = eˣ"},
    {"id": "numeric.edo.decaimiento", "operation": "numeric.rk45",
     "params": {"expressions": ["-2*y"], "state_vars": ["y"], "t0": 0, "t1": 3, "y0": [1]},
     "path": "value.y.-1.0", "expected": math.exp(-6), "tol": 1e-9, "reference": "y = e^{−2t}"},
    {"id": "numeric.edo.oscilador_rk45", "operation": "numeric.solve_ivp",
     "params": {"expressions": ["v", "-x"], "state_vars": ["x", "v"], "t0": 0, "t1": "2*pi", "y0": [1, 0]},
     "path": "value.y.-1.0", "expected": 1.0, "tol": 1e-7, "check_error_estimate": True,
     "reference": "oscilador armónico x'' = −x: x(2π) = cos(2π) = 1"},
    {"id": "numeric.edo.oscilador_rk4", "operation": "numeric.rk4",
     "params": {"expressions": ["v", "-x"], "state_vars": ["x", "v"], "t0": 0, "t1": "2*pi", "y0": [1, 0],
                "steps": 400},
     "path": "value.y.-1.1", "expected": 0.0, "tol": 1e-8, "check_error_estimate": True,
     "reference": "oscilador armónico: v(2π) = −sin(2π) = 0"},

    # --- linalg --------------------------------------------------------
    {"id": "linalg.solve.3x3", "operation": "linalg.solve",
     "params": {"A": [[2, 1, -1], [-3, -1, 2], [-2, 1, 2]], "b": [8, -11, -3]},
     "path": "x", "expected": [2.0, 3.0, -1.0], "tol": 1e-12, "reference": "ejemplo clásico de eliminación gaussiana"},
    {"id": "linalg.det.3x3", "operation": "linalg.det",
     "params": {"A": [[6, 1, 1], [4, -2, 5], [2, 8, 7]]}, "path": "value", "expected": -306.0, "tol": 1e-10,
     "reference": "regla de Sarrus"},
    {"id": "linalg.inversa.2x2", "operation": "linalg.inverse", "params": {"A": [[4, 7], [2, 6]]},
     "path": "value", "expected": [[0.6, -0.7], [-0.2, 0.4]], "tol": 1e-14, "reference": "fórmula de la adjunta"},
    {"id": "linalg.eig.tridiagonal", "operation": "linalg.eig_symmetric",
     "params": {"A": [[2, -1, 0], [-1, 2, -1], [0, -1, 2]]}, "path": "value.values",
     "expected": [2 - math.sqrt(2), 2.0, 2 + math.sqrt(2)], "tol": 1e-13,
     "reference": "λ_k = 2 − 2cos(kπ/4)"},
    {"id": "linalg.lstsq.recta", "operation": "linalg.lstsq",
     "params": {"A": [[1, 0], [1, 1], [1, 2]], "b": [1, 2, 2]}, "path": "x",
     "expected": [7 / 6, 0.5], "tol": 1e-14, "reference": "ecuaciones normales resueltas a mano"},
    {"id": "linalg.cross.ij", "operation": "linalg.cross", "params": {"u": [1, 0, 0], "v": [0, 1, 0]},
     "path": "value", "expected": [0.0, 0.0, 1.0], "tol": 0, "reference": "î × ĵ = k̂"},
    {"id": "linalg.norm.fro", "operation": "linalg.norm", "params": {"x": [[1, 2], [3, 4]], "ord": "fro"},
     "path": "value", "expected": math.sqrt(30), "tol": 1e-15, "reference": "√(1+4+9+16)"},

    # --- poly ----------------------------------------------------------
    {"id": "poly.raices.cubica", "operation": "poly.roots", "params": {"p": [1, -6, 11, -6]},
     "path": "value", "expected": [{"re": 1.0, "im": 0.0}, {"re": 2.0, "im": 0.0}, {"re": 3.0, "im": 0.0}],
     "tol": 1e-12, "reference": "(x−1)(x−2)(x−3)"},
    {"id": "poly.raices.complejas", "operation": "poly.roots", "params": {"p": [1, 0, 1]},
     "path": "value", "expected": [{"re": 0.0, "im": -1.0}, {"re": 0.0, "im": 1.0}], "tol": 1e-14,
     "reference": "x² + 1 = 0 → ±i"},
    {"id": "poly.raiz_doble", "operation": "poly.roots", "params": {"p": [1, 2, 1]},
     "path": "value", "expected": [{"re": -1.0, "im": 0.0}, {"re": -1.0, "im": 0.0}], "tol": 1e-7,
     "reference": "(x+1)²: raíz doble, precisión ~√eps"},
    {"id": "poly.polyval.horner", "operation": "poly.polyval", "params": {"p": [2, -6, 2, -1], "x": 3},
     "path": "value", "expected": 5.0, "tol": 0, "reference": "2·27 − 6·9 + 2·3 − 1"},
    {"id": "poly.polyfit.cuadratica", "operation": "poly.polyfit",
     "params": {"x": [0, 1, 2, 3, 4], "y": [1, 3, 7, 13, 21], "degree": 2}, "path": "coefficients",
     "expected": [1.0, 1.0, 1.0], "tol": 1e-12, "reference": "datos exactos de x² + x + 1"},

    # --- stats ---------------------------------------------------------
    {"id": "stats.std.poblacional", "operation": "stats.std",
     "params": {"data": [2, 4, 4, 4, 5, 5, 7, 9], "ddof": 0}, "path": "value", "expected": 2.0, "tol": 1e-15,
     "reference": "ejemplo clásico: σ = 2"},
    {"id": "stats.mediana.par", "operation": "stats.median", "params": {"data": [3, 1, 4, 1, 5, 9, 2, 6]},
     "path": "value", "expected": 3.5, "tol": 0, "reference": "(3 + 4)/2"},
    {"id": "stats.regresion.exacta", "operation": "stats.linregress",
     "params": {"x": [0, 1, 2, 3], "y": [1, 3, 5, 7]}, "path": "slope", "expected": 2.0, "tol": 1e-14,
     "reference": "y = 2x + 1 exacta"},

    # --- vector (Mat C) ------------------------------------------------
    {"id": "vector.rotor.rotacion", "operation": "vector.curl",
     "params": {"field": ["-y", "x", "0"], "variables": ["x", "y", "z"], "point": [1, 2, 3]},
     "path": "value", "expected": [0.0, 0.0, 2.0], "tol": 0, "reference": "∇×(−y, x, 0) = (0, 0, 2)"},
    {"id": "vector.rotor.gradiente_nulo", "operation": "vector.curl",
     "params": {"field": ["2x*y", "x^2 + 2y*z", "y^2"], "variables": ["x", "y", "z"], "point": [1, -1, 2]},
     "path": "value", "expected": [0.0, 0.0, 0.0], "tol": 0,
     "reference": "rot(∇φ) = 0 con φ = x²y + y²z"},
    {"id": "vector.divergencia.radial", "operation": "vector.divergence",
     "params": {"field": ["x", "y", "z"], "variables": ["x", "y", "z"], "point": [5, -2, 7]},
     "path": "value", "expected": [3.0], "tol": 0, "reference": "∇·r = 3"},
    {"id": "vector.gradiente.r2", "operation": "vector.gradient",
     "params": {"expression": "x^2 + y^2 + z^2", "variables": ["x", "y", "z"], "point": [1, 2, 3]},
     "path": "value", "expected": [2.0, 4.0, 6.0], "tol": 0, "reference": "∇r² = 2r"},
    {"id": "vector.laplaciano.armonica", "operation": "vector.laplacian",
     "params": {"expression": "x^2 - y^2", "variables": ["x", "y"], "point": [3, 4]},
     "path": "value", "expected": [0.0], "tol": 0, "reference": "x² − y² es armónica"},
    {"id": "vector.jacobiano.polares", "operation": "vector.jacobian",
     "params": {"field": ["r*cos(t)", "r*sin(t)"], "variables": ["r", "t"], "point": [2, 0]},
     "path": "value", "expected": [[1.0, 0.0], [0.0, 2.0]], "tol": 1e-15, "reference": "det J = r en polares"},

    # --- signals (Mat D) -----------------------------------------------
    {"id": "signals.fft.impulso", "operation": "signals.fft", "params": {"x": [1, 0, 0, 0]},
     "path": "value", "expected": [{"re": 1.0, "im": 0.0}] * 4, "tol": 1e-15, "reference": "DFT(δ) = 1"},
    {"id": "signals.fft.coseno", "operation": "signals.fft", "params": {"x": [1, 0, -1, 0]},
     "path": "value.1", "expected": {"re": 2.0, "im": 0.0}, "tol": 1e-15, "reference": "cos(πn/2): X[1] = N/2"},
    {"id": "signals.espectro.senoidal", "operation": "signals.spectrum",
     "params": {"expression": "3*sin(2*pi*50*t)", "sample_rate": 1024, "n": 1024},
     "path": "amplitude.50", "expected": 3.0, "tol": 1e-9, "reference": "senoidal de amplitud 3 en bin exacto"},
    {"id": "signals.tf.polos", "operation": "signals.transfer_function",
     "params": {"num": [1], "den": [1, 3, 2]}, "path": "poles",
     "expected": [{"re": -2.0, "im": 0.0}, {"re": -1.0, "im": 0.0}], "tol": 1e-12,
     "reference": "1/((s+1)(s+2))"},
    {"id": "signals.tf.estabilidad", "operation": "signals.transfer_function",
     "params": {"num": [1], "den": [1, -1]}, "path": "stability", "expected": "inestable",
     "reference": "polo en s = +1"},
    {"id": "signals.bode.primer_orden", "operation": "signals.bode",
     "params": {"num": [1], "den": [1, 1], "w": [1]}, "path": "magnitude_db.0",
     "expected": -10 * math.log10(2), "tol": 1e-12, "reference": "1/(s+1) en ω = 1: −3.0103 dB"},
    {"id": "signals.bode.fase", "operation": "signals.bode",
     "params": {"num": [1], "den": [1, 1], "w": [1]}, "path": "phase_deg.0",
     "expected": -45.0, "tol": 1e-12, "reference": "1/(s+1) en ω = 1: −45°"},

    # --- units (Capa 3) ------------------------------------------------
    {"id": "units.torque.imperial", "operation": "units.convert",
     "params": {"value": 1, "from": "kN*m", "to": "lbf*ft"}, "path": "value",
     "expected": 737.5621, "tol": 1e-4, "reference": "1 kN·m = 737.5621 lbf·ft (tablas)"},
    {"id": "units.temperatura.fahrenheit", "operation": "units.convert",
     "params": {"value": 100, "from": "degC", "to": "degF"}, "path": "value", "expected": 212.0, "tol": 1e-12,
     "reference": "ebullición del agua"},
    {"id": "units.presion.psi", "operation": "units.convert",
     "params": {"value": 1, "from": "atm", "to": "psi"}, "path": "value", "expected": 14.6959, "tol": 1e-4,
     "reference": "1 atm = 14.6959 psi"},
    {"id": "units.velocidad.nudos", "operation": "units.convert",
     "params": {"value": 100, "from": "kn", "to": "km/h"}, "path": "value", "expected": 185.2, "tol": 1e-10,
     "reference": "1 kn = 1.852 km/h (definición)"},
    {"id": "units.energia.kwh", "operation": "units.analyze", "params": {"unit": "kW*h"},
     "path": "factor_to_si", "expected": 3.6e6, "tol": 1e-6, "reference": "1 kWh = 3.6 MJ"},
    {"id": "units.dimension.newton", "operation": "units.analyze", "params": {"unit": "kg*m/s^2"},
     "path": "dimension", "expected": "L·M·T^-2", "reference": "dimensión de la fuerza"},

    # --- errores esperados --------------------------------------------
    {"id": "error.ln_negativo_real", "operation": "expr.evaluate", "params": {"expression": "ln(-1)"},
     "expect_error": "DOMAIN_ERROR", "reference": "ln(−1) no es real"},
    {"id": "error.sqrt_negativo_real", "operation": "expr.evaluate", "params": {"expression": "sqrt(-4)"},
     "expect_error": "DOMAIN_ERROR", "reference": "√−4 no es real"},
    {"id": "error.division_cero", "operation": "expr.evaluate", "params": {"expression": "1/(x-2)",
                                                                          "variables": {"x": 2}},
     "expect_error": "DOMAIN_ERROR", "reference": "1/0"},
    {"id": "error.sintaxis", "operation": "expr.parse", "params": {"expression": "2*(x+"},
     "expect_error": "PARSE_ERROR", "reference": "paréntesis sin cerrar"},
    {"id": "error.variable_indefinida", "operation": "expr.evaluate", "params": {"expression": "x + 1"},
     "expect_error": "EVALUATION_ERROR", "reference": "x sin valor"},
    {"id": "error.matriz_singular", "operation": "linalg.solve",
     "params": {"A": [[1, 2], [2, 4]], "b": [1, 2]}, "expect_error": "SINGULAR_MATRIX",
     "reference": "filas linealmente dependientes"},
    {"id": "error.dimensiones_matmul", "operation": "linalg.matmul",
     "params": {"A": [[1, 2]], "B": [[1, 2]]}, "expect_error": "DIMENSION_ERROR", "reference": "1×2 · 1×2"},
    {"id": "error.unidades_incompatibles", "operation": "units.convert",
     "params": {"value": 1, "from": "N", "to": "J"}, "expect_error": "DIMENSION_ERROR",
     "reference": "fuerza ≠ energía"},
    {"id": "error.suma_inconsistente", "operation": "units.check_consistency",
     "params": {"terms": ["m", "s"]}, "expect_error": "DIMENSION_ERROR", "reference": "m + s no tiene sentido"},
    {"id": "error.sin_cambio_de_signo", "operation": "numeric.bisection",
     "params": {"expression": "x^2 + 1", "a": -1, "b": 1}, "expect_error": "DOMAIN_ERROR",
     "reference": "x² + 1 no tiene raíces reales"},
    {"id": "error.newton_derivada_nula", "operation": "numeric.newton",
     "params": {"expression": "x^2 + 1", "x0": 0}, "expect_error": "CONVERGENCE_ERROR",
     "reference": "f'(0) = 0"},
    {"id": "error.integral_singular", "operation": "numeric.simpson_adaptive",
     "params": {"expression": "1/x", "a": 0, "b": 1}, "expect_error": "DOMAIN_ERROR",
     "reference": "1/x no es integrable en 0"},
    {"id": "error.operacion_desconocida", "operation": "no.existe", "params": {},
     "expect_error": "UNKNOWN_OPERATION", "reference": "contrato de la API"},
    {"id": "error.parametro_faltante", "operation": "numeric.brent", "params": {"expression": "x"},
     "expect_error": "INVALID_INPUT", "reference": "contrato de la API"},
]


# --- comparación -------------------------------------------------------

def _extract(result, path):
    node = result
    for part in path.split(".") if path else []:
        if isinstance(node, list):
            node = node[int(part)]
        else:
            node = node[part]
    return node


def _deviation(expected, got):
    """Máxima desviación absoluta entre estructuras; ``None`` si no son comparables."""
    if isinstance(expected, str):
        return 0.0 if expected == got else None
    if isinstance(expected, (int, float)) and not isinstance(expected, bool):
        if isinstance(got, dict) and set(got) == {"re", "im"}:
            got = complex(got["re"], got["im"])
            return abs(got - expected)
        if isinstance(got, (int, float)) and not isinstance(got, bool):
            return abs(got - expected)
        return None
    if isinstance(expected, dict):
        if not isinstance(got, dict) or set(got) != set(expected):
            return None
        devs = [_deviation(expected[k], got[k]) for k in expected]
    elif isinstance(expected, list):
        if not isinstance(got, list) or len(got) != len(expected):
            return None
        devs = [_deviation(e, g) for e, g in zip(expected, got)]
    else:
        return None
    if any(d is None for d in devs):
        return None
    return max(devs, default=0.0)


def run_case(case):
    """Ejecuta un caso y devuelve una fila de resultados (dict JSON-compatible)."""
    response = run(case["operation"], case["params"])
    row = {
        "id": case["id"], "module": case["operation"].split(".", 1)[0], "operation": case["operation"],
        "reference": case.get("reference", ""), "elapsed_ms": response["elapsed_ms"],
    }
    if "expect_error" in case:
        got_code = None if response["ok"] else response["error"]["code"]
        row.update(expected=f"error {case['expect_error']}", got=f"error {got_code}" if got_code else "sin error",
                   deviation=None, passed=got_code == case["expect_error"])
        return row
    row["expected"] = case["expected"]
    if not response["ok"]:
        err = response["error"]
        row.update(got=f"error {err['code']}: {err['message']}", deviation=None, passed=False)
        return row
    try:
        got = _extract(response["result"], case.get("path", ""))
    except (KeyError, IndexError, ValueError, TypeError):
        row.update(got=f"ruta {case.get('path')!r} inexistente", deviation=None, passed=False)
        return row
    dev = _deviation(case["expected"], got)
    tol = case.get("tol", 0.0)
    if case.get("rel") and isinstance(case["expected"], (int, float)):
        tol *= abs(case["expected"])
    passed = dev is not None and dev <= tol
    if passed and case.get("check_error_estimate"):
        est = response["result"].get("error_estimate")
        if isinstance(est, (int, float)) and dev > 10 * est + tol:
            passed = False
            row["note"] = f"el error real {dev:.3g} supera 10× el estimado {est:.3g}"
    row.update(got=got, deviation=dev, tol=tol, passed=passed)
    return row


def run_all(module=None):
    rows = [run_case(c) for c in CASES if module is None or c["operation"].split(".", 1)[0] == module]
    passed = sum(r["passed"] for r in rows)
    return {"total": len(rows), "passed": passed, "failed": len(rows) - passed, "cases": rows}


def _short(value, width=34):
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    return text if len(text) <= width else text[: width - 1] + "…"


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if "--export" in argv:
        path = argv[argv.index("--export") + 1]
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(CASES, fh, ensure_ascii=False, indent=2)
        print(f"{len(CASES)} casos exportados a {path}")
        return 0
    module = argv[argv.index("--module") + 1] if "--module" in argv else None
    report = run_all(module)
    for r in report["cases"]:
        mark = "PASA " if r["passed"] else "FALLA"
        dev = "" if r["deviation"] is None else f"{r['deviation']:.2e}"
        print(f"{mark} {r['id']:<36} esp={_short(r['expected']):<34} obt={_short(r['got']):<34} {dev}")
        if r.get("note"):
            print(f"      ↳ {r['note']}")
    print(f"\n{report['passed']}/{report['total']} casos pasan")
    return 0 if report["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
