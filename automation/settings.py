from urllib.parse import urlparse


def validar_url_local(url):
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or parsed.hostname not in ("127.0.0.1", "localhost"):
        raise ValueError("Execução recusada: a URL deve apontar para localhost ou 127.0.0.1.")
    if parsed.port not in (None, 5000):
        raise ValueError("Execução recusada: use a porta local 5000.")
    return url.rstrip("/")

