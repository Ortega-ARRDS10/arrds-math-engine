"""Capa 1: parser, evaluador y álgebra simbólica."""

import math
import unittest

from arrds_math.errors import DomainError, EvaluationError, ParseError
from arrds_math.expr import compile_function, derivative, evaluate, parse, simplify, to_latex, to_string


class TestParser(unittest.TestCase):
    def test_precedencia_y_asociatividad(self):
        self.assertEqual(evaluate("2^3^2"), 512.0)          # asociativa por la derecha
        self.assertEqual(evaluate("-2^2"), -4.0)
        self.assertEqual(evaluate("2**3"), 8.0)
        self.assertEqual(evaluate("10 - 4 - 3"), 3.0)
        self.assertEqual(evaluate("3!"), 6.0)

    def test_multiplicacion_implicita(self):
        env = {"x": 3.0}
        self.assertEqual(evaluate("2x", env), 6.0)
        self.assertEqual(evaluate("2(x+1)", env), 8.0)
        self.assertEqual(evaluate("x(x+1)", env), 12.0)
        self.assertEqual(evaluate("(x)(x)", env), 9.0)
        self.assertAlmostEqual(evaluate("2 sin(x)", env), 2 * math.sin(3.0))

    def test_errores_de_sintaxis(self):
        for bad in ("", "2*(x+", "3 +", "x $ 2", ")", "2 3"):
            with self.subTest(expr=bad), self.assertRaises(ParseError):
                parse(bad)

    def test_limites_de_entrada(self):
        with self.assertRaises(ParseError):
            parse("x+" * 6000 + "1")               # demasiado larga
        with self.assertRaises(ParseError):
            parse("(" * 150 + "1" + ")" * 150)     # demasiado anidada
        self.assertEqual(evaluate("(" * 90 + "1" + ")" * 90), 1.0)  # dentro del límite

    def test_to_string_ida_y_vuelta(self):
        for text in ("a - (b + c)", "a / (b * c)", "(-2)^x", "-(x^2)", "sin(x)^2"):
            with self.subTest(text=text):
                node = parse(text)
                self.assertEqual(parse(to_string(node)), node)


class TestEvaluador(unittest.TestCase):
    def test_modo_real_rechaza_complejos(self):
        for expr in ("ln(-1)", "sqrt(-1)", "(-8)^(1/3)", "asin(2)"):
            with self.subTest(expr=expr), self.assertRaises(DomainError):
                evaluate(expr)

    def test_modo_complejo(self):
        self.assertAlmostEqual(evaluate("ln(-1)", complex_mode=True), complex(0, math.pi))
        self.assertAlmostEqual(abs(evaluate("exp(j*pi) + 1", complex_mode=True)), 0.0, places=15)
        self.assertEqual(evaluate("abs(3 + 4j)", complex_mode=True), 5.0)

    def test_errores_de_evaluacion(self):
        with self.assertRaises(EvaluationError):
            evaluate("x + 1")
        with self.assertRaises(EvaluationError):
            evaluate("sin(1, 2)")
        with self.assertRaises(DomainError):
            evaluate("1/0")
        with self.assertRaises(DomainError):
            evaluate("171!")

    def test_log_es_natural(self):
        self.assertAlmostEqual(evaluate("log(e)"), 1.0)
        self.assertAlmostEqual(evaluate("log(8, 2)"), 3.0)
        self.assertAlmostEqual(evaluate("log10(1000)"), 3.0)

    def test_compile_function(self):
        f = compile_function("x^2 + y", ["x", "y"])
        self.assertEqual(f(3, 1), 10.0)
        with self.assertRaises(EvaluationError):
            compile_function("x + z", ["x"])


class TestSimbolico(unittest.TestCase):
    def check_derivative(self, expr, x0):
        """Contrasta la derivada simbólica con diferencias centradas."""
        d = compile_function(derivative(expr, "x"), ["x"])
        f = compile_function(expr, ["x"])
        h = 1e-6
        self.assertAlmostEqual(d(x0), (f(x0 + h) - f(x0 - h)) / (2 * h), places=5, msg=expr)

    def test_derivadas_contra_diferencias(self):
        for expr in ("x^3 - 2x", "sin(x)*cos(x)", "exp(-x^2)", "ln(x)/x", "x^x", "atan(x)",
                     "sqrt(1 + x^2)", "tanh(2x)", "2^x", "asin(x/2)", "log(x, 10)", "hypot(x, 2)"):
            with self.subTest(expr=expr):
                self.check_derivative(expr, 0.7)

    def test_simplificacion_conservadora(self):
        self.assertEqual(to_string(simplify(parse("0*x + 1*y"))), "y")
        self.assertEqual(to_string(simplify(parse("x - x"))), "0")
        # No cancela x/x: cambiaría el dominio (x = 0).
        self.assertEqual(to_string(simplify(parse("x/x"))), "x / x")

    def test_latex(self):
        self.assertEqual(to_latex("x^2/2"), r"\frac{{x}^{2}}{2}")
        self.assertEqual(to_latex("sqrt(alpha)"), r"\sqrt{\alpha}")
        self.assertEqual(to_latex("2x"), "2 x")


if __name__ == "__main__":
    unittest.main()
