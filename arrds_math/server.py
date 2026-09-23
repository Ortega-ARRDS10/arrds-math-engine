"""Servidor local del panel de pruebas (banco de pruebas, no el producto final).

    python -m arrds_math.server [--port 8765]

Sirve ``web/index.html`` y tres endpoints JSON:

* ``GET  /api/operations`` — catálogo de operaciones (``api.list_operations``).
* ``POST /api/run``        — ``{"operation": "...", "params": {...}}`` → respuesta uniforme.
* ``POST /api/selftest``   — ``{"module": "units"?}`` → informe del banco de verificación.

Seguridad: escucha solo en 127.0.0.1, limita el tamaño del cuerpo, exige
JSON, rechaza ``Host``/``Origin`` ajenos (protección contra DNS rebinding
y CSRF desde otras páginas) y nunca evalúa código: toda expresión pasa
por el parser del motor.
"""

import argparse
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from . import api, selftest

HOST = "127.0.0.1"
DEFAULT_PORT = 8765
MAX_BODY = 1 << 20  # 1 MiB
MAX_DRAIN = 8 << 20  # cuerpo que se descarta antes de responder 413 (ver _drain)
WEB_DIR = Path(__file__).with_name("web")

_CSP = ("default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; "
        "connect-src 'self'; img-src data:; base-uri 'none'; form-action 'none'; frame-ancestors 'none'")


class Handler(BaseHTTPRequestHandler):
    server_version = "ArrdsMathEngine/" + api.API_VERSION
    sys_version = ""
    timeout = 30  # segundos por operación de socket: un cliente colgado no bloquea un hilo para siempre

    # --- utilidades --------------------------------------------------
    def _send(self, status, body, content_type):
        data = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Referrer-Policy", "no-referrer")
        if content_type.startswith("text/html"):
            self.send_header("Content-Security-Policy", _CSP)
            self.send_header("X-Frame-Options", "DENY")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(data)

    def _json(self, status, payload):
        self._send(status, json.dumps(payload, ensure_ascii=False, allow_nan=False),
                   "application/json; charset=utf-8")

    def _error(self, status, code, message):
        self._json(status, {"ok": False, "error": {"code": code, "message": message}, "elapsed_ms": 0})

    def _trusted_origin(self):
        """Solo se aceptan peticiones dirigidas a este mismo servidor local."""
        port = self.server.server_address[1]
        allowed = {f"127.0.0.1:{port}", f"localhost:{port}"}
        if self.headers.get("Host") not in allowed:
            return False
        origin = self.headers.get("Origin")
        return origin is None or origin in {f"http://{h}" for h in allowed}

    def _read_json(self):
        if "json" not in (self.headers.get("Content-Type") or ""):
            self._error(415, "INVALID_INPUT", "Se requiere Content-Type: application/json")
            return None
        try:
            length = int(self.headers.get("Content-Length", ""))
        except ValueError:
            self._error(411, "INVALID_INPUT", "Falta Content-Length")
            return None
        if length < 0 or length > MAX_BODY:
            self._drain(length)
            self._error(413, "INVALID_INPUT", f"Cuerpo demasiado grande (máx. {MAX_BODY} bytes)")
            return None
        try:
            body = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            self._error(400, "INVALID_INPUT", f"JSON inválido: {exc}")
            return None
        if not isinstance(body, dict):
            self._error(400, "INVALID_INPUT", "El cuerpo debe ser un objeto JSON")
            return None
        return body

    def _drain(self, length):
        """Descarta (sin guardar) un cuerpo rechazado, acotado a MAX_DRAIN.

        Si se cierra la conexión con datos sin leer, algunos sistemas (Windows)
        la resetean y el cliente nunca ve el 413. Por encima de MAX_DRAIN no se
        lee nada: se responde y se cierra.
        """
        if not 0 < length <= MAX_DRAIN:
            return
        remaining = length
        try:
            while remaining > 0:
                chunk = self.rfile.read(min(remaining, 1 << 16))
                if not chunk:
                    break
                remaining -= len(chunk)
        except OSError:
            pass

    # --- rutas -------------------------------------------------------
    def do_GET(self):
        if not self._trusted_origin():
            return self._error(403, "FORBIDDEN", "Origen no permitido")
        path = self.path.split("?", 1)[0]
        if path in ("/", "/index.html"):
            return self._send(200, (WEB_DIR / "index.html").read_bytes(), "text/html; charset=utf-8")
        if path == "/api/operations":
            return self._json(200, api.list_operations())
        return self._error(404, "NOT_FOUND", f"Ruta desconocida: {path}")

    do_HEAD = do_GET

    def do_POST(self):
        if not self._trusted_origin():
            return self._error(403, "FORBIDDEN", "Origen no permitido")
        path = self.path.split("?", 1)[0]
        if path not in ("/api/run", "/api/selftest"):
            return self._error(404, "NOT_FOUND", f"Ruta desconocida: {path}")
        body = self._read_json()
        if body is None:
            return None
        if path == "/api/run":
            name = body.get("operation")
            if not isinstance(name, str):
                return self._error(400, "INVALID_INPUT", "Falta 'operation' (texto)")
            return self._json(200, api.run(name, body.get("params", {})))
        module = body.get("module")
        if module is not None and module not in api.MODULES:
            return self._error(400, "INVALID_INPUT", f"Módulo desconocido: {module!r}")
        return self._json(200, selftest.run_all(module))

    def log_message(self, fmt, *args):
        sys.stderr.write(f"[arrds] {self.command} {self.path} → {args[1] if len(args) > 1 else ''}\n")


def make_server(port=DEFAULT_PORT):
    return ThreadingHTTPServer((HOST, port), Handler)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Panel de pruebas del motor matemático de Arrds Studio")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args(argv)
    server = make_server(args.port)
    print(f"Arrds Math Engine — panel de pruebas en http://{HOST}:{args.port}  (Ctrl+C para salir)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
