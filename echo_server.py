import socket
from http.server import BaseHTTPRequestHandler
from io import BytesIO
import urllib.parse


def parse_status(status_param):
    try:
        status_code = int(status_param)
        status_phrase = BaseHTTPRequestHandler.responses.get(status_code, 'Unknown Status')
        return f"{status_code} {status_phrase}"
    except (ValueError, TypeError):
        return "200 OK"


def parse_request(request):
    request_line, headers_alone = request.split('\r\n', 1)
    headers = headers_alone.split('\r\n')
    method, path, version = request_line.split()
    return method, path, headers


def handle_client_connection(client_socket):
    request = client_socket.recv(1024).decode('utf-8')
    method, path, headers = parse_request(request)

    # Extract status parameter from the path
    query = urllib.parse.urlparse(path).query
    query_params = urllib.parse.parse_qs(query)
    status_param = query_params.get('status', ['200'])[0]
    response_status = parse_status(status_param)

    # Formulate the response
    response_body = f"Request Method: {method}\n"
    response_body += f"Request Source: {client_socket.getpeername()}\n"
    response_body += f"Response Status: {response_status}\n"
    for header in headers:
        response_body += header + "\n"

    response = (
        f"HTTP/1.1 {response_status}\r\n"
        f"Content-Length: {len(response_body)}\r\n"
        f"Content-Type: text/plain\r\n"
        f"\r\n"
        f"{response_body}"
    )

    client_socket.sendall(response.encode('utf-8'))
    client_socket.close()


def start_server(host='0.0.0.0', port=8080):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Listening on {host}:{port}...")

    while True:
        client_socket, addr = server_socket.accept()
        handle_client_connection(client_socket)


if __name__ == "__main__":
    start_server()
