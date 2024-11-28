import socket
import pickle

class SimpleSocket:
    def __init__(self, host='localhost', port=8080, is_server=False):
        """
        Initialize the socket.
        :param host: Hostname or IP address
        :param port: Port number
        :param is_server: True for server, False for client
        """
        self.host = host
        self.port = port
        self.is_server = is_server
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if is_server:
            self.sock.bind((self.host, self.port))
            self.sock.listen(5)  # Max 5 clients
            print(f"Server listening on {self.host}:{self.port}")

    def send(self, message, connection=None):
        """
        Send a message through the socket.
        :param message: Message to send (string)
        :param connection: Connection object (for server use)
        """
        if type(message) == str:
            message = message.encode()
        if self.is_server and connection:
            connection.sendall(message)
        else:
            self.sock.sendall(message)

    def receive(self, connection=None, buffer_size=4096):
        """
        Receive a message through the socket.
        :param connection: Connection object (for server use)
        :param buffer_size: Size of the receive buffer
        :return: Received message (string)
        """
        if self.is_server and connection:
            data = connection.recv(buffer_size)
        else:
            data = self.sock.recv(buffer_size)
        try:
            data = data.decode()
        except UnicodeDecodeError as e:
            data = pickle.loads(data)
        return data

    def accept_connection(self):
        """
        Accept a new client connection (server only).
        :return: Client connection and address
        """
        if not self.is_server:
            raise Exception("accept_connection can only be used on a server socket.")
        connection, address = self.sock.accept()
        print(f"Accepted connection from {address}")
        return connection, address

    def connect(self):
        """
        Connect to the server (client only).
        """
        if self.is_server:
            raise Exception("connect can only be used on a client socket.")
        self.sock.connect((self.host, self.port))
        print(f"Connected to server at {self.host}:{self.port}")

    def close(self):
        """
        Close the socket.
        """
        self.sock.close()
        print("Socket closed")



def start_server(host, port, data=None):
    server = SimpleSocket(host=host, port=port, is_server=True)
    conn, addr = server.accept_connection()
    if data:
        data = pickle.dumps(data)
        server.send(data, connection=conn)
    while True:
        message = server.receive(connection=conn)
        if message:
            response = message
        else:
            break
        print(f"Received from client: {response}")
    server.close()
    return response

def start_client(host, port, data=None):
    client = SimpleSocket(host=host, port=port, is_server=False)
    client.connect()
    response = client.receive()
    if data:
        data = pickle.dumps(data)
        client.send(data)
    print(f"Received from server: {response}")
    client.close()
    return response
