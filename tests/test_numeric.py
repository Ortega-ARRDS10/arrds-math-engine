"""Capa 2: raíces, derivación, integración y EDO."""

import math
import unittest

from arrds_math.errors import ConvergenceError, DomainError, InvalidInputError
from arrds_math.numeric import (
    IterativeResult, bisection, brent, derivative, find_root, gauss_legendre, newton, rk4, rk45,
    secant, simpson_adaptive, solve_ivp, system_from_expressions, trapezoid,
)

WALLIS = 2.0945514815423265


class TestRaices(unittest.TestCase):
    def test_todos_los_metodos(self):
        for res in (bisection("x^3-2x-5", 2, 3), newton("x^3-2x-5", 2), secant("x^3-2x-5", 2, 3),
                    brent("x^3-2x-5", 2, 3), find_root("x^3-2x-5", a=2, b=3)):
            with self.subTest(method=res.method):
                self.assertIsInstance(res, IterativeResult)
                self.assertTrue(res.converged)
                self.assertGreater(res.iterations, 0)
                self.assertAlmostEqual(res.value, WALLIS, places=11)
                self.assertLessEqual(abs(res.value - WALLIS), 10 * res.error_estimate + 1e-12)

    def test_funciones_python(self):
        self.assertAlmostEqual(brent(math.cos, 0, 2).value, math.pi / 2, places=12)
        self.assertAlmostEqual(newton(lambda x: x * x - 2, 1).value, math.sqrt(2), places=12)

    def test_fallos_con_pista(self):
        with self.assertRaises(DomainError) as ctx:
            bisection("x^2 + 1", -1, 1)
        self.assertIn("Bolzano", ctx.exception.hint)
        with self.assertRaises(ConvergenceError) as ctx:
            newton("x^2 + 1", 0)
        self.assertTrue(ctx.exception.hint)
        with self.assertRaises(InvalidInputError):
            find_root("x", method="magia", a=0, b=1)
        with self.assertRaises(InvalidInputError):
            brent("x", -1, 1, tol=-1)


class TestCalculo(unittest.TestCase):
    def test_derivada_numerica(self):
        res = derivative("sin(x)", 1.0)
        self.assertAlmostEqual(res.value, math.cos(1.0), places=10)
        self.assertAlmostEqual(derivative("x^3", 2.0, order=2).value, 12.0, places=6)

    def test_integrales(self):
        self.assertAlmostEqual(simpson_adaptive("sin(x)", 0, math.pi).value, 2.0, places=9)
        self.assertAlmostEqual(simpson_adaptive("x", 1, 1).value, 0.0)
        self.assertAlmostEqual(simpson_adaptive("x^2", 1, 0).value, -1 / 3, places=10)  # límites invertidos
        self.assertAlmostEqual(gauss_legendre("x^7", -1, 1, n=4).value, 0.0, places=14)  # exacta grado ≤ 7
        self.assertAlmostEqual(gauss_legendre("exp(x)", 0, 1).value, math.e - 1, places=14)

    def test_integral_singular_falla(self):
        with self.assertRaises((DomainError, ConvergenceError)):
            simpson_adaptive("1/sqrt(x)", 0, 1)

    def test_trapecio(self):
        self.assertEqual(trapezoid([0, 1, 2]), 2.0)
        self.assertEqual(trapezoid([0, 1, 4], x=[0, 1, 2]), 3.0)
        with self.assertRaises(InvalidInputError):
            trapezoid([1])


class TestEDO(unittest.TestCase):
    def setUp(self):
        self.osc = system_from_expressions(["v", "-x"], ["x", "v"])

    def test_oscilador_rk45(self):
        res = rk45(self.osc, 0, [1, 0], 2 * math.pi)
        x, v = res.value["y"][-1]
        self.assertAlmostEqual(x, 1.0, places=7)
        self.assertAlmostEqual(v, 0.0, places=7)
        self.assertTrue(res.converged)
        self.assertLessEqual(abs(x - 1.0), 10 * res.error_estimate + 1e-12)

    def test_oscilador_rk4_error_estimado(self):
        res = rk4(self.osc, 0, [1, 0], 2 * math.pi, steps=100)
        x, v = res.value["y"][-1]
        err = max(abs(x - 1.0), abs(v))   # el estimado es la norma máx. sobre componentes
        self.assertLess(err, 1e-5)
        # La estimación por duplicación de paso debe ser del orden del error real.
        self.assertLess(err, 10 * res.error_estimate)
        self.assertGreater(err, res.error_estimate / 10)

    def test_hacia_atras_y_despachador(self):
        res = solve_ivp(lambda t, y: [-y[0]], 1, [math.exp(-1)], 0)
        self.assertAlmostEqual(res.value["y"][-1][0], 1.0, places=8)
        with self.assertRaises(InvalidInputError):
            solve_ivp(self.osc, 0, [1, 0], 1, method="euler")

    def test_divergencia_detectada(self):
        with self.assertRaises(ConvergenceError) as ctx:
            rk45(lambda t, y: [y[0] ** 2], 0, [1], 2)   # y = 1/(1−t) explota en t = 1
        self.assertTrue(ctx.exception.hint)


if __name__ == "__main__":
    unittest.main()
