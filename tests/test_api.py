"""Contrato JSON de la API, banco de verificación y servidor del panel."""

import http.client
import json
import math
import threading
import unittest

from arrds_math import api, selftest, server


class TestContrato(unittest.TestCase):
    def test_todos_los_ejemplos_funcionan_y_son_json_estricto(self):
        for name, op in api.OPERATIONS.items():
            with self.subTest(operation=name):
                res = api.run(name, op.example)
                self.assertTrue(res["ok"], res.get("error"))
                self.assertEqual(set(res), {"ok", "operation", "result", "elapsed_ms"})
                json.dumps(res, allow_nan=False)  # sin NaN/Infinity crudos

    def test_cada_modulo_tiene_operaciones(self):
        modules = {op.module for op in api.OPERATIONS.values()}
        self.assertEqual(modules, set(api.MODULES))
        catalog = api.list_operations()
        self.assertEqual(len(catalog["operations"]), len(api.OPERATIONS))

    def test_serializacion(self):
        self.assertEqual(api.to_jsonable(complex(1, -2)), {"re": 1.0, "im": -2.0})
        self.assertEqual(api.to_jsonable([math.inf, -math.inf, math.nan]), ["inf", "-inf", "nan"])
        self.assertEqual(api.from_jsonable_number({"re": 1, "im": 2}, allow_complex=True), complex(1, 2))
        self.assertEqual(api.from_jsonable_number("inf"), math.inf)

    def test_errores_tipados(self):
        cases = {
            ("expr.evaluate", '{"expression": "ln(-1)"}'): "DOMAIN_ERROR",
            ("no.existe", "{}"): "UNKNOWN_OPERATION",
            ("numeric.brent", '{"expression": "x"}'): "INVALID_INPUT",
            ("numeric.brent", '{"expression": "x", "a": -1, "b": 1, "sobra": 1}'): "INVALID_INPUT",
            ("linalg.det", '{"A": [[1, true]]}'): "INVALID_INPUT",
            ("linalg.solve", '{"A": [[1, 2], [2, 4]], "b": [1, 2]}'): "SINGULAR_MATRIX",
            ("units.convert", '{"value": 1, "from": "N", "to": "J"}'): "DIMENSION_ERROR",
        }
        for (name, params), code in cases.items():
            with self.subTest(operation=name, params=params):
                res = api.run(name, json.loads(params))
                self.assertFalse(res["ok"])
                self.assertEqual(res["error"]["code"], code)
                self.assertIn("elapsed_ms", res)

    def test_limites_de_tamano(self):
        big = [[1.0] * (api.MAX_MATRIX_DIM + 1)]
        self.assertEqual(api.run("linalg.transpose", {"A": big})["error"]["code"], "INVALID_INPUT")
        res = api.run("expr.sample", {"expression": "x", "a": 0, "b": 1, "n": api.MAX_SAMPLES + 1})
        self.assertEqual(res["error"]["code"], "INVALID_INPUT")

    def test_iterativos_reportan_error(self):
        for name in ("numeric.brent", "numeric.newton", "numeric.simpson_adaptive", "numeric.rk45",
                     "numeric.rk4", "poly.roots", "linalg.eig_symmetric"):
            with self.subTest(operation=name):
                result = api.run(name, api.OPERATIONS[name].example)["result"]
                for key in ("value", "converged", "iterations", "error_estimate", "method"):
                    self.assertIn(key, result)

    def test_series_para_graficar(self):
        res = api.run("signals.bode", api.OPERATIONS["signals.bode"].example)["result"]
        self.assertEqual(len(res["plots"]), 2)
        self.assertTrue(res["plots"][0]["log_x"])
        sample = api.run("expr.sample", {"expression": "ln(x)", "a": -1, "b": 1, "n": 5})["result"]
        self.assertIsNone(sample["y"][0])          # fuera de dominio → null, no excepción
        self.assertGreater(sample["undefined_points"], 0)


class TestBancoDeVerificacion(unittest.TestCase):
    def test_todos_los_casos_pasan(self):
        for case in selftest.CASES:
            with self.subTest(case=case["id"]):
                row = selftest.run_case(case)
                self.assertTrue(row["passed"], f"esperado {row['expected']!r}, obtenido {row['got']!r}")

    def test_casos_son_json_puro_e_ids_unicos(self):
        json.dumps(selftest.CASES, allow_nan=False)
        ids = [c["id"] for c in selftest.CASES]
        self.assertEqual(len(ids), len(set(ids)))
        for c in selftest.CASES:
            self.assertIn("reference", c, c["id"])
            self.assertTrue(("expected" in c) != ("expect_error" in c), c["id"])

    def test_detecta_fallas(self):
        falso = {"id": "x", "operation": "expr.evaluate", "params": {"expression": "1+1"},
                 "path": "value", "expected": 3.0, "tol": 1e-12}
        self.assertFalse(selftest.run_case(falso)["passed"])


class TestServidor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        server.Handler.log_message = lambda *a: None
        cls.srv = server.make_server(0)  # puerto libre
        cls.port = cls.srv.server_address[1]
        cls.thread = threading.Thread(target=cls.srv.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.srv.server_close()

    def request(self, method, path, body=None, headers=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=30)
        hdrs = {"Content-Type": "application/json"}
        hdrs.update(headers or {})
        data = body if isinstance(body, (bytes, type(None))) else json.dumps(body).encode()
        conn.request(method, path, body=data, headers=hdrs)
        res = conn.getresponse()
        payload = res.read()
        conn.close()
        return res.status, payload, res

    def test_solo_localhost(self):
        self.assertEqual(self.srv.server_address[0], "127.0.0.1")

    def test_index_y_operaciones(self):
        status, body, res = self.request("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn("Content-Security-Policy", res.headers)
        self.assertNotIn(b"eval(", body)
        status, body, _ = self.request("GET", "/api/operations")
        self.assertEqual(len(json.loads(body)["operations"]), len(api.OPERATIONS))

    def test_run_y_selftest(self):
        status, body, _ = self.request("POST", "/api/run",
                                       {"operation": "units.convert", "params": {"value": 1, "from": "kN*m", "to": "lbf*ft"}})
        self.assertEqual(status, 200)
        self.assertAlmostEqual(json.loads(body)["result"]["value"], 737.5621, places=4)
        status, body, _ = self.request("POST", "/api/selftest", {"module": "units"})
        rep = json.loads(body)
        self.assertEqual(rep["failed"], 0)
        self.assertTrue(all(c["module"] == "units" for c in rep["cases"]))

    def test_protecciones(self):
        status, _, _ = self.request("POST", "/api/run", b"x" * (server.MAX_BODY + 1))
        self.assertEqual(status, 413)
        # Solo la cabecera: se rechaza sin esperar el cuerpo.
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=30)
        conn.putrequest("POST", "/api/run")
        conn.putheader("Content-Type", "application/json")
        conn.putheader("Content-Length", str(server.MAX_DRAIN + 1))
        conn.endheaders()
        self.assertEqual(conn.getresponse().status, 413)
        conn.close()
        status, _, _ = self.request("POST", "/api/run", b"{no es json")
        self.assertEqual(status, 400)
        status, _, _ = self.request("POST", "/api/run", {"operation": "expr.evaluate"}, {"Content-Type": "text/plain"})
        self.assertEqual(status, 415)
        status, _, _ = self.request("POST", "/api/run", {"operation": "x"}, {"Origin": "http://evil.example"})
        self.assertEqual(status, 403)
        status, _, _ = self.request("GET", "/api/operations", headers={"Host": "evil.example"})
        self.assertEqual(status, 403)
        status, _, _ = self.request("GET", "/../arrds_math/api.py")
        self.assertEqual(status, 404)


if __name__ == "__main__":
    unittest.main()
