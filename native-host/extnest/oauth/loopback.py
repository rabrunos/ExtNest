import base64, hashlib, secrets, threading, urllib.parse, webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler

def pkce_pair():
    verifier = secrets.token_urlsafe(64)[:96]
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return verifier, challenge

class LoopbackReceiver:
    def __init__(self, public_host="127.0.0.1", timeout=300):
        self.public_host = public_host
        self.timeout = timeout
        self.result = None
        self.server = None

    def __enter__(self):
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                pass

            def do_GET(self):
                query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
                owner.result = {k: v[0] for k, v in query.items()}
                body = b"""<!doctype html><meta charset=utf-8>
                <title>ExtNest</title><style>body{font:16px Segoe UI,sans-serif;padding:40px;max-width:680px;margin:auto}</style>
                <h1>ExtNest conectado</h1><p>Voce pode fechar esta aba e voltar ao ExtNest.</p>"""
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        self.server = HTTPServer(("127.0.0.1", 0), Handler)
        self.server.timeout = self.timeout
        return self

    @property
    def port(self):
        return self.server.server_address[1]

    @property
    def redirect_uri(self):
        return f"http://{self.public_host}:{self.port}"

    def open_and_wait(self, authorization_url):
        webbrowser.open(authorization_url, new=1, autoraise=True)
        self.server.handle_request()
        if not self.result:
            raise RuntimeError("Tempo de autenticação esgotado.")
        return self.result

    def __exit__(self, exc_type, exc, tb):
        if self.server:
            self.server.server_close()
