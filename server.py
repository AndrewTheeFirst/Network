from utils import ServerSocket, ClientSocket, background_process
from consts import HOST, PORT,\
      IN, OUT, BAD, GOOD

class Host:
    def __init__(self, sock: ClientSocket, addr: tuple[str, int]):
        self.sock = sock
        self.ip = addr[0]
        self.name = ""
        self.connected = True
    
    def give(self, message: str, flag: str = OUT) -> str:
        '''
        Main method of communication to host following host initlization. If IN flag is used, receive method must also be called!'''
        if not self.connected:
            print(f"This host is no longer connected. (give, {message}, {flag})")
            return BAD
        elif self.sock.give(message, flag) == BAD:
            self.disconnect()
            return BAD
        return GOOD

    def receive(self) -> str:
        if not self.connected:
            print("This host is no longer connected.")
            return BAD
        else:
            message = self.sock.receive()
            if message == BAD:
                self.disconnect()
        return message

    def disconnect(self):
        self.connected = False
        self.sock.close()
        print(f"{self} has disconnected")
    
    def connnect(self):
        self.connected = True
        print(f"{self} has connected.")
    
    def set_name(self) -> str:
        self.give("Enter a username: ", IN)
        self.name = self.receive()
        return self.name

    def __str__(self):
        return f"[{self.name}, {self.ip}]"

class Server:
    def __init__(self, serv_addr: tuple[str, int] = (HOST, PORT), max_conn: int = 1):
        '''
        Args:
            serv_addr (tuple[str, int]): the public ip address and the socket of the server
            max_conn (int): the maximum connections allowed by the server'''
        self.server_socket = ServerSocket()
        # binds the server to the ip and port specified
        self.server_socket.bind(serv_addr)
        # sets the maximum connections
        self.server_socket.listen(max_conn)
        self.hosts: list[Host] = []
        self.accepting = False
    
    def open(self):
        print("Server is now open.")
        self.accepting = True
        self.accept_clients()

    def close(self):
        print("Server is now closed")
        self.accepting = False

    def give_all(self, message: str):
        for host in self.hosts:
            host.give(message)

    @background_process
    def accept_clients(self):
        while True:
            host_socket, host_addr = self.server_socket.accept()
            if self.accepting:
                ip = host_addr[0]
                if ip in self._get_host_ips():
                    host = self._get_host_by_ip(ip)
                    host.sock = host_socket # update to most current socket
                    host.connnect()
                    host.give(f"Welcome back {host.name}!\n")
                else:
                    self.setup_host(host_socket, host_addr)
    
    def setup_host(self, host_socket: ClientSocket, host_addr: tuple[str, int]):
        host = Host(host_socket, host_addr)
        while host.set_name() in self._get_host_names():
            host.sock.give("That name is taken!\n")
        if host.name == BAD:
            print("A Host failed to connect")
        else:
            print(f"{host} has connected.")
            self.hosts.append(host)
            host.give(f"Welcome {host.name}!\n")
    
    def _get_host_names(self):
        return [host.name for host in self.hosts]

    def _get_host_ips(self) -> list[str]:
        return [host.ip for host in self.hosts]
    
    def _get_host_by_ip(self, ip: str):
        for host in self.hosts:
            if host.ip == ip:
                return host
        raise IndexError(f"No Host found by IP: {ip}")

if __name__ == "__main__":
    server = Server()
    server.open()