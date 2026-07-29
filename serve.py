#!/usr/bin/env python3
"""
MAKERTON · LIVE RELAY — local HTTPS server.

Phone cameras only open in a secure context, so plain http://192.168.x.x
will silently fail. This serves the folder over HTTPS with a self-signed
certificate and prints the LAN address to open on the PC.

    python serve.py            # https://<lan-ip>:8443
    python serve.py 9000       # custom port

Needs: pip install cryptography   (or an `openssl` binary on PATH)
"""

import http.server
import ipaddress
import os
import socket
import ssl
import subprocess
import sys
import webbrowser

try:  # Korean console output on legacy Windows code pages
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
CERT = os.path.join(HERE, "cert.pem")
KEY = os.path.join(HERE, "key.pem")
ARGS = [a for a in sys.argv[1:] if a]
PORT = next((int(a) for a in ARGS if a.isdigit()), 8443)
FORCE_IP = next((a for a in ARGS if not a.isdigit()), None)

# Subnets handed out by phone hotspots — these beat a wired default route,
# because the phone can only reach the PC on its own network.
HOTSPOT_PREFIXES = (
    "192.168.43.",   # Android
    "172.20.10.",    # iPhone
    "192.168.137.",  # Windows Mobile Hotspot
    "192.168.49.",   # Android Wi-Fi Direct
)


def route_ip() -> str:
    """IP of the interface holding the default route."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def all_ips() -> list:
    found = []
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ip = info[4][0]
            if not ip.startswith("127.") and ip not in found:
                found.append(ip)
    except OSError:
        pass
    primary = route_ip()
    if primary != "127.0.0.1" and primary not in found:
        found.insert(0, primary)
    return found or ["127.0.0.1"]


def lan_ip() -> str:
    """Best address for the phone to reach this PC."""
    if FORCE_IP:
        return FORCE_IP
    ips = all_ips()
    for ip in ips:
        if ip.startswith(HOTSPOT_PREFIXES):
            return ip
    primary = route_ip()
    return primary if primary != "127.0.0.1" else ips[0]


def make_cert(ip: str) -> None:
    """Self-signed cert valid for localhost and this machine's LAN IP."""
    try:
        import datetime

        from cryptography import x509
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.x509.oid import NameOID
    except ImportError:
        if not make_cert_openssl(ip):
            sys.exit(
                "인증서를 만들 수 없습니다.\n"
                "  pip install cryptography\n"
                "를 실행한 뒤 다시 시도하세요."
            )
        return

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "makerton-live-relay")])
    alt = [x509.DNSName("localhost"), x509.IPAddress(ipaddress.ip_address("127.0.0.1"))]
    try:
        alt.append(x509.IPAddress(ipaddress.ip_address(ip)))
    except ValueError:
        pass

    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(days=1))
        .not_valid_after(now + datetime.timedelta(days=825))
        .add_extension(x509.SubjectAlternativeName(alt), critical=False)
        .sign(key, hashes.SHA256())
    )

    with open(KEY, "wb") as f:
        f.write(
            key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.TraditionalOpenSSL,
                serialization.NoEncryption(),
            )
        )
    with open(CERT, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    print("· 자체 서명 인증서를 생성했습니다 (cert.pem / key.pem)")


def make_cert_openssl(ip: str) -> bool:
    try:
        subprocess.run(
            [
                "openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes",
                "-keyout", KEY, "-out", CERT, "-days", "825",
                "-subj", "/CN=makerton-live-relay",
                "-addext", f"subjectAltName=DNS:localhost,IP:127.0.0.1,IP:{ip}",
            ],
            check=True,
            capture_output=True,
        )
        print("· openssl로 인증서를 생성했습니다")
        return True
    except (OSError, subprocess.CalledProcessError):
        return False


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=HERE, **kw)

    def end_headers(self):
        # always serve the freshest file during a live demo
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        pass  # keep the console clean for the presentation


def main() -> None:
    ip = lan_ip()
    if not (os.path.exists(CERT) and os.path.exists(KEY)):
        make_cert(ip)

    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(CERT, KEY)

    httpd = http.server.ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)

    url = f"https://{ip}:{PORT}/index.html"
    others = [x for x in all_ips() if x != ip]

    print()
    print("  MAKERTON · LIVE RELAY")
    print("  ─────────────────────────────────────────────")
    print(f"  PC 뷰어   {url}")
    print()
    print("  1. 이 창은 그대로 두세요. (닫으면 방송이 끊깁니다)")
    print("  2. 브라우저 경고 → 고급 → 계속 진행")
    print("  3. 화면의 QR을 폰 카메라로 찍기")
    print("  4. 폰에서도 경고 → 계속 진행 → 카메라 허용 → 방송 시작")
    print()
    print("  · 종료: 이 창에서 Ctrl+C")

    if others:
        print()
        print("  ┌ QR을 찍었는데 폰에서 페이지가 안 열리면,")
        print("  │ 아래 주소로 다시 실행하세요:")
        for x in others:
            print(f"  │    python serve.py {PORT} {x}")
        print("  └")
    print()

    try:
        webbrowser.open(url)
    except Exception:
        pass

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n종료합니다.")
        httpd.server_close()


if __name__ == "__main__":
    main()
