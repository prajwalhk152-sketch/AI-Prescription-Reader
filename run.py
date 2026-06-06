import socket

import uvicorn


def find_port(start_port=8000, max_attempts=20):
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(("127.0.0.1", port))
            except OSError:
                continue
            return port

    raise RuntimeError("No free local port found.")


if __name__ == "__main__":
    port = find_port()
    print(f"AI Prescription Reader running at http://127.0.0.1:{port}")
    uvicorn.run("api.api_server:app", host="127.0.0.1", port=port)
