"""Capa 2: álgebra lineal, polinomios y estadística."""

import math
import unittest

from arrds_math import linalg, poly, stats
from arrds_math.errors import DimensionError, InvalidInputError, SingularMatrixError


def close(a, b, tol=1e-12):
    if isinstance(a, list):
        return len(a) == len(b) and all(close(x, y, tol) for x, y in zip(a, b))
    return abs(a - b) <= tol


class TestLinalg(unittest.TestCase):
    A = [[4.0, -2.0, 1.0], [-2.0, 4.0, -2.0], [1.0, -2.0, 4.0]]

    def test_solve_y_residuo(self):
        b = [11.0, -16.0, 17.0]
        x = linalg.solve(self.A, b)
        self.assertTrue(close(linalg.matvec(self.A, x), b))

    def test_lu_reconstruye(self):
        f = linalg.lu(self.A)
        pa = [self.A[i] for i in f["P"]]
        self.assertTrue(close(linalg.matmul(f["L"], f["U"]), pa))

    def test_inversa_y_det(self):
        inv = linalg.inverse(self.A)
        self.assertTrue(close(linalg.matmul(self.A, inv), linalg.identity(3)))
        self.assertAlmostEqual(linalg.det([[1, 2], [3, 4]]), -2.0)
        self.assertEqual(linalg.det([[1, 2], [2, 4]]), 0.0)

    def test_qr_ortogonal(self):
        a = [[12, -51, 4], [6, 167, -68], [-4, 24, -41]]
        f = linalg.qr(a)
        q = f["Q"]
        self.assertTrue(close(linalg.matmul(linalg.transpose(q), q), linalg.identity(3)))
        self.assertTrue(close(linalg.matmul(q, f["R"]), [[float(v) for v in r] for r in a], 1e-10))

    def test_eig_simetrica(self):
        res = linalg.eig_symmetric(self.A)
        self.assertTrue(res.converged)
        vals, vecs = res.value["values"], res.value["vectors"]
        for k, lam in enumerate(vals):
            v = [row[k] for row in vecs]
            self.assertTrue(close(linalg.matvec(self.A, v), [lam * t for t in v], 1e-12))
        with self.assertRaises(InvalidInputError):
            linalg.eig_symmetric([[1, 2], [3, 4]])

    def test_normas_y_cond(self):
        self.assertAlmostEqual(linalg.norm([3, 4]), 5.0)
        self.assertEqual(linalg.norm([1, -7, 2], "inf"), 7.0)
        self.assertAlmostEqual(linalg.norm([[3, 0], [0, 4]], 2), 4.0)
        self.assertEqual(linalg.cond([[1, 2], [2, 4]]), math.inf)
        self.assertAlmostEqual(linalg.cond(linalg.identity(4)), 1.0)

    def test_errores(self):
        with self.assertRaises(SingularMatrixError) as ctx:
            linalg.solve([[1, 2], [2, 4]], [1, 2])
        self.assertTrue(ctx.exception.hint)
        with self.assertRaises(DimensionError):
            linalg.solve([[1, 2, 3], [4, 5, 6]], [1, 2])
        with self.assertRaises(DimensionError):
            linalg.cross([1, 2], [3, 4])
        with self.assertRaises(InvalidInputError):
            linalg.as_matrix([[1, "a"]])


class TestPoly(unittest.TestCase):
    def test_aritmetica(self):
        self.assertEqual(poly.polymul([1, 1], [1, -1]), [1.0, 0.0, -1.0])
        self.assertEqual(poly.polyadd([1, 0, 1], [-1, 3]), [1.0, -1.0, 4.0])
        self.assertEqual(poly.polyder([1, 0, -3, 2]), [3, 0, -3])
        self.assertEqual(poly.polyint([3, 0, 1], k=2), [1.0, 0.0, 1.0, 2])
        self.assertEqual(poly.polyval([1, -3, 2], 1j), complex(1, -3))

    def test_raices(self):
        res = poly.roots([1, -6, 11, -6])
        self.assertTrue(close([r.real for r in res.value], [1.0, 2.0, 3.0]))
        self.assertTrue(all(r.imag == 0 for r in res.value))
        self.assertEqual(poly.roots([1, 0, 0]).value, [0j, 0j])  # raíces nulas exactas

    def test_raiz_multiple_error_honesto(self):
        res = poly.roots([1, -3, 3, -1])  # (x − 1)³
        worst = max(abs(r - 1) for r in res.value)
        self.assertLessEqual(worst, res.error_estimate)

    def test_polyfit(self):
        fit = poly.polyfit([0, 1, 2, 3], [1, 3, 5, 7], 1)
        self.assertTrue(close(fit["coefficients"], [2.0, 1.0]))
        self.assertAlmostEqual(fit["r2"], 1.0)
        with self.assertRaises(InvalidInputError):
            poly.polyfit([0, 1], [0, 1], 3)


class TestStats(unittest.TestCase):
    def test_descriptiva(self):
        d = stats.describe([2, 4, 4, 4, 5, 5, 7, 9])
        self.assertEqual(d["mean"], 5.0)
        self.assertEqual(d["median"], 4.5)
        self.assertAlmostEqual(d["std"], math.sqrt(32 / 7))
        self.assertAlmostEqual(d["sem"], d["std"] / math.sqrt(8))
        self.assertNotIn("std", stats.describe([1]))

    def test_regresion_con_incertidumbre(self):
        r = stats.linregress([0, 1, 2, 3, 4], [0.1, 2.1, 3.9, 6.2, 7.9])
        self.assertAlmostEqual(r["slope"], 1.97, places=12)  # Sxy/Sxx = 19.7/10
        self.assertGreater(r["slope_stderr"], 0)
        self.assertGreater(r["r2"], 0.99)
        with self.assertRaises(InvalidInputError):
            stats.linregress([1, 1], [2, 3])

    def test_errores(self):
        with self.assertRaises(InvalidInputError):
            stats.mean([])
        with self.assertRaises(InvalidInputError):
            stats.variance([1])


if __name__ == "__main__":
    unittest.main()
