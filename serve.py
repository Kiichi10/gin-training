#!/usr/bin/env python3
"""HTTPS server for 銀トレ games. Also serves CA cert for iPhone installation."""
import http.server
import ssl
import os

PORT = 8080
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GAME_DIR = os.path.join(BASE_DIR, "games", "01_ふうふうトレイン")
CERT = os.path.join(BASE_DIR, "cert.pem")
KEY = os.path.join(BASE_DIR, "key.pem")
CA_CERT = os.path.join(BASE_DIR, "ca-cert.pem")


class GameHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=GAME_DIR, **kwargs)

    def do_GET(self):
        # /ca.pem でCA証明書をダウンロードさせる
        if self.path == '/ca.pem':
            with open(CA_CERT, 'rb') as f:
                data = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'application/x-x509-ca-cert')
            self.send_header('Content-Disposition', 'attachment; filename="GinTrainCA.pem"')
            self.send_header('Content-Length', len(data))
            self.end_headers()
            self.wfile.write(data)
            return
        super().do_GET()


context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(CERT, KEY)

server = http.server.HTTPServer(("0.0.0.0", PORT), GameHandler)
server.socket = context.wrap_socket(server.socket, server_side=True)

print(f"🚂 ふうふうトレイン HTTPS server running!")
print(f"   PC:     https://localhost:{PORT}")
print(f"   スマホ: https://192.168.11.39:{PORT}")
print(f"")
print(f"📱 iPhone設定手順:")
print(f"   1. Safariで http://192.168.11.39:{PORT + 1}/ca.pem を開いてCA証明書をインストール")
print(f"   2. 設定 → 一般 → VPNとデバイス管理 → GinTrain Local CA → インストール")
print(f"   3. 設定 → 一般 → 情報 → 証明書信頼設定 → GinTrain Local CA を有効に")
print(f"   4. Safariで https://192.168.11.39:{PORT} を開く")
server.serve_forever()
