"""Mat C (vectorial), Mat D (señales) y Capa 3 (unidades)."""

import math
import unittest

from arrds_math import signals, units, vector
from arrds_math.errors import DimensionError, InvalidInputError

XYZ = ["x", "y", "z"]


class TestVector(unittest.TestCase):
    def test_rotor(self):
        r = vector.curl(["-y", "x", "0"], XYZ, point=[1, 2, 3])
        self.assertEqual(r["expressions"], ["0", "0", "2"])
        self.assertEqual(r["value"], [0.0, 0.0, 2.0])

    def test_identidades(self):
        # div(rot F) = 0 para un campo cualquiera
        rot = vector.curl(["x^2*y", "y*z^3", "sin(x*z)"], XYZ)["expressions"]
        self.assertEqual(vector.divergence(rot, XYZ, point=[0.3, -1.2, 2.0])["value"], [0.0])
        # rot(grad f) = 0
        grad = vector.gradient("x*y*z + exp(x)", XYZ)["expressions"]
        self.assertEqual(vector.curl(grad, XYZ, point=[1, 2, 3])["value"], [0.0, 0.0, 0.0])

    def test_laplaciano_y_jacobiano(self):
        self.assertEqual(vector.laplacian("x^2 + y^2 + z^2", XYZ, point=[1, 1, 1])["value"], [6.0])
        j = vector.jacobian(["r*cos(t)", "r*sin(t)"], ["r", "t"], point=[2, math.pi / 2])["value"]
        self.assertAlmostEqual(j[0][0] * j[1][1] - j[0][1] * j[1][0], 2.0)  # det J = r
        self.assertTrue(vector.gradient("x^2", ["x"])["latex"][0])

    def test_errores(self):
        with self.assertRaises(DimensionError):
            vector.curl(["x", "y"], ["x", "y"])
        with self.assertRaises(DimensionError):
            vector.gradient("x", ["x", "y"], point=[1])


class TestSignals(unittest.TestCase):
    def test_fft_ida_y_vuelta(self):
        x = [1.0, 2.0, -1.0, 0.5, 3.0, 0.0, -2.0, 1.0]
        back = signals.fft(signals.fft(x), inverse=True)
        self.assertTrue(all(abs(a - b) < 1e-12 for a, b in zip(x, back)))

    def test_dft_no_potencia_de_2_coincide(self):
        x = [1.0, 2.0, 3.0]
        X = signals.fft(x)
        self.assertAlmostEqual(X[0], 6.0)
        self.assertAlmostEqual(X[1], complex(-1.5, math.sqrt(3) / 2))
        with self.assertRaises(InvalidInputError):
            signals.fft([0.0] * (signals.MAX_DFT + 1))

    def test_espectro_amplitud(self):
        fs, n = 64, 64
        x = [2 * math.cos(2 * math.pi * 5 * k / fs) for k in range(n)]
        s = signals.spectrum(x, fs)
        self.assertAlmostEqual(s["amplitude"][5], 2.0)
        self.assertEqual(s["frequency"][5], 5.0)

    def test_funcion_de_transferencia(self):
        tf = signals.transfer_function([1, 2], [1, 3, 2])
        self.assertEqual(tf["stability"], "estable")
        self.assertAlmostEqual(tf["dc_gain"], 1.0)
        self.assertEqual(signals.transfer_function([1], [1, 0, 1])["stability"], "marginalmente estable")

    def test_bode_segundo_orden(self):
        # Resonancia de 1/(s² + 2ζs + 1) en ω = 1: |H| = 1/(2ζ)
        zeta = 0.1
        r = signals.freq_response([1], [1, 2 * zeta, 1], w=[1.0, 100.0])
        self.assertAlmostEqual(r["magnitude_db"][0], 20 * math.log10(1 / (2 * zeta)))
        self.assertAlmostEqual(r["phase_deg"][0], -90.0)
        self.assertLess(r["phase_deg"][1], -179.0)  # fase desenvuelta, no salta a +180


class TestUnits(unittest.TestCase):
    def test_conversiones(self):
        self.assertAlmostEqual(units.convert(1, "kN*m", "lbf*ft"), 737.5621, places=4)
        self.assertAlmostEqual(units.convert(1, "mi", "km"), 1.609344)
        self.assertAlmostEqual(units.convert(1, "hp", "W"), 745.6998715822702)
        self.assertAlmostEqual(units.convert(1, "MPa", "N/mm^2"), 1.0)
        self.assertAlmostEqual(units.convert(3000, "rpm", "rad/s"), 100 * math.pi)
        self.assertAlmostEqual(units.convert(1, "µm", "m"), 1e-6)

    def test_temperatura(self):
        self.assertAlmostEqual(units.convert(-40, "degC", "degF"), -40.0)
        self.assertAlmostEqual(units.convert(0, "degC", "K"), 273.15)
        with self.assertRaises(DimensionError):
            units.convert(1, "degC", "m")

    def test_analisis_dimensional(self):
        a = units.analyze("kg*m/s^2")
        self.assertEqual(a["dimension"], "L·M·T^-2")
        self.assertEqual(a["si_unit"], "m*kg*s^-2")
        self.assertEqual(units.analyze("J/N")["dimension"], "L")

    def test_consistencia_y_errores(self):
        self.assertTrue(units.check_consistency(["N*m", "J", "kW*h"])["consistent"])
        with self.assertRaises(DimensionError):
            units.check_consistency(["N", "J"])
        with self.assertRaises(DimensionError):
            units.convert(1, "N", "J")
        with self.assertRaises(InvalidInputError):
            units.parse_unit("furlong")
        with self.assertRaises(InvalidInputError):
            units.parse_unit("m + s")


if __name__ == "__main__":
    unittest.main()
