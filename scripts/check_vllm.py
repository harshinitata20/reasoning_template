import socket
import urllib.parse
import requests
from config.settings import settings

def check():
    url = settings.VLLM_BASE_URL
    print("VLLM URL:", url)
    parsed = urllib.parse.urlparse(url)
    host = parsed.hostname
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    print(f"Checking TCP {host}:{port}...")
    try:
        sock = socket.create_connection((host, port), timeout=5)
        sock.close()
        print("TCP: open")
    except Exception as e:
        print("TCP: error:", repr(e))

    print("Attempting HTTP POST (5s timeout)...")
    try:
        payload = {"model": settings.VLLM_MODEL, "messages": [{"role":"user","content":"ping"}]}
        r = requests.post(url, json=payload, timeout=5)
        print("HTTP status:", r.status_code)
        print("Response snippet:", r.text[:400])
    except Exception as e:
        print("HTTP error:", repr(e))

if __name__ == '__main__':
    check()
