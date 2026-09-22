import base64, hashlib, secrets, urllib.parse, webbrowser
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

                # Remove OAuth parameters from the visible URL immediately.
                # Then try to close the tab. Browsers can block window.close()
                # for tabs they do not consider script-opened, so keep a clean
                # fallback page in that case.
                body = b"""<!doctype html>
<meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>ExtNest conectado</title>
<style>
  :root{color-scheme:light dark}
  body{font:15px/1.5 "Segoe UI",system-ui,sans-serif;margin:0;display:grid;place-items:center;min-height:100vh;background:Canvas;color:CanvasText}
  main{max-width:520px;padding:32px;text-align:center}
  h1{font-size:22px;margin:0 0 8px}
  p{opacity:.75;margin:0}
  button{margin-top:18px;padding:9px 14px;border:1px solid ButtonBorder;border-radius:8px;background:ButtonFace;color:ButtonText;cursor:pointer}
</style>
<main>
  <h1>ExtNest conectado</h1>
  <p id="status">Finalizando conexao...</p>
  <button id="closeBtn" type="button">Fechar esta aba</button>
</main>
<script>
  try {
    history.replaceState(null, "", "/");
  } catch {}

  const closeTab = () => {
    try { window.close(); } catch {}
  };

  document.getElementById("closeBtn").addEventListener("click", closeTab);

  setTimeout(closeTab, 120);
  setTimeout(() => {
    if (!window.closed) {
      document.getElementById("status").textContent =
        "Conexao concluida. Voce pode fechar esta aba e voltar ao ExtNest.";
    }
  }, 700);
</script>"""
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
                self.send_header("Pragma", "no-cache")
                self.send_header("Referrer-Policy", "no-referrer")
                self.send_header("X-Content-Type-Options", "nosniff")
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
