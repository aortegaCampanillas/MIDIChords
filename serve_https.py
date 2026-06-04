#!/usr/bin/env python3
"""
HTTPS server para servir la aplicación web de MIDIChords.
Permite probar características que requieren HTTPS (como Web MIDI API con permisos persistentes).

Uso: python serve_https.py [--port 8443] [--cert cert.pem] [--key key.pem]
"""

import http.server
import ssl
import argparse
import os
import sys
import urllib.request
import json
from pathlib import Path

class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler con soporte CORS y SPA routing."""

    def __init__(self, *args, directory=None, **kwargs):
        super().__init__(*args, directory=directory, **kwargs)

    def end_headers(self):
        """Añade headers CORS a todas las respuestas."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        super().end_headers()

    def do_GET(self):
        """Handle GET requests con soporte para SPAs y rutas dinámicas."""
        # Proxy de API a backend
        if self.path.startswith('/api/'):
            return self._proxy_api_request('GET')

        # Rutas SPA conocidas
        spa_routes = {
            '/app': '/app.html',
            '/fp30x': '/fp30x.html',
        }

        # Si es una ruta SPA, servir el HTML correspondiente
        if self.path in spa_routes:
            self.path = spa_routes[self.path]
        elif self.path == '/':
            self.path = '/index.html'
        elif not '.' in self.path.split('/')[-1]:
            # Si no tiene extensión, probablemente sea una ruta SPA
            # Intentar servir como archivo primero
            file_path = self.translate_path(self.path)
            if not Path(file_path).exists():
                # Si no existe como archivo, usar index.html (SPA fallback)
                self.path = '/index.html'

        # Servir archivos estáticos
        return super().do_GET()

    def do_POST(self):
        """Handle POST requests (API proxy)."""
        if self.path.startswith('/api/'):
            return self._proxy_api_request('POST')
        self.send_error(405)

    def _proxy_api_request(self, method):
        """Proxy API requests to backend server."""
        backend_url = f'http://localhost:8000{self.path}'

        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else b''

            req = urllib.request.Request(backend_url, data=body, method=method)
            req.add_header('Content-Type', self.headers.get('Content-Type', 'application/json'))

            with urllib.request.urlopen(req) as response:
                response_data = response.read()
                self.send_response(response.status)
                self.send_header('Content-Type', response.headers.get('Content-Type', 'application/json'))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response_data)
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_data = json.dumps({'error': str(e)}).encode()
            self.wfile.write(error_data)
        except Exception as e:
            print(f'[API Proxy Error] {method} {self.path}: {e}')
            self.send_response(502)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_data = json.dumps({'error': 'Backend unavailable'}).encode()
            self.wfile.write(error_data)

    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax."""
        # Usar la implementación del padre pero retornar el path
        return super().translate_path(path)

    def log_message(self, format, *args):
        """Log messages en formato más legible."""
        print(f'[{self.client_address[0]}] {format % args}')

def main():
    parser = argparse.ArgumentParser(
        description='HTTPS server para servir la aplicación web de MIDIChords'
    )
    parser.add_argument('--port', type=int, default=8443,
                       help='Puerto a usar (default: 8443)')
    parser.add_argument('--cert', default='.certs/cert.pem',
                       help='Path al certificado SSL (default: .certs/cert.pem)')
    parser.add_argument('--key', default='.certs/key.pem',
                       help='Path a la clave privada SSL (default: .certs/key.pem)')

    args = parser.parse_args()

    # Cambiar al directorio de la aplicación web
    web_dir = Path(__file__).parent / 'apps' / 'web'
    if not web_dir.exists():
        print(f'❌ Error: No se encontró el directorio {web_dir}')
        sys.exit(1)

    # Verificar certificados
    cert_path = Path(args.cert)
    key_path = Path(args.key)

    if not cert_path.exists():
        print(f'❌ Error: Certificado no encontrado: {cert_path}')
        print('Genera los certificados con:')
        print('  mkdir -p .certs')
        print('  openssl req -x509 -newkey rsa:2048 -keyout .certs/key.pem -out .certs/cert.pem -days 365 -nodes -subj "/CN=localhost"')
        sys.exit(1)

    if not key_path.exists():
        print(f'❌ Error: Clave privada no encontrada: {key_path}')
        sys.exit(1)

    # Crear servidor HTTPS
    handler = lambda *args, **kwargs: CORSRequestHandler(*args, directory=str(web_dir), **kwargs)

    # Crear servidor HTTP base
    server = http.server.HTTPServer(('0.0.0.0', args.port), handler)

    # Configurar SSL
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(str(cert_path), str(key_path))
    server.socket = context.wrap_socket(server.socket, server_side=True)

    # Mostrar información prominente
    print()
    print('=' * 70)
    print('🔒 ¡SERVIDOR HTTPS INICIADO!')
    print('=' * 70)
    print(f'   📍 Frontend URL: https://localhost:{args.port}')
    print(f'   🔌 Backend API: http://localhost:8000/api/ (con proxy)')
    print(f'   📁 Directorio: {web_dir}')
    print(f'   🔐 Certificado: {cert_path}')
    print()
    print('⚠️  ADVERTENCIA DE SEGURIDAD DEL NAVEGADOR')
    print('   El navegador mostrará una advertencia porque el certificado')
    print('   es auto-firmado. Esto es NORMAL en desarrollo.')
    print()
    print('   ✅ Haz clic en "Avanzado" o "Continuar de todas formas"')
    print()
    print('💡 Para usar este servidor con el backend:')
    print('   Lanza la configuración "Web: MIDIChords (HTTPS + Backend)"')
    print('   desde VS Code o ejecuta en otra terminal:')
    print('   python launch.py web --host 0.0.0.0 --port 8000')
    print()
    print('=' * 70)
    print('Presiona Ctrl+C para detener el servidor...')
    print('=' * 70)
    print()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n✓ Servidor detenido')
        sys.exit(0)

if __name__ == '__main__':
    main()
