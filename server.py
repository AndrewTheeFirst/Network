from .sockets import ServerSocket, ClientSocket
from .utils import asynchronus
from .consts import HOST, PORT,\
      IN, OUT, BAD, GOOD
from time import sleep
from _socket import MSG_PEEK
import select

class Host:
    def __init__(self, sock: ClientSocket, addr: tuple[str, int]):
        '''
        Args:
            sock (ClientSocket): the actual socket returned when any client connects to the server
            addr (tuple[str, int]): the actual address returned when any client connects to the server'''
        self.sock = sock
        self.ip = addr[0]
        self.name = ""
        self.connected = True
    
    def give(self, message: str | object, flag: str = OUT) -> str:
        '''
        Is the method of communication to host following host initlization. If IN flag is used, receive 
        method must also be called! Returns BAD if any errors occur, otherwise returns GOOD.'''
        ret = BAD
        end = "\n" if flag == OUT else ""
        message = message if isinstance(message, str) else str(message)
        if not self.connected:
            # print(f"This host is no longer connected.")
            ...
        elif self.sock.give(message + end, flag) == BAD:
            self.disconnect()
        else:
            ret = GOOD
        return ret

    def receive(self) -> str:
        '''Called when expecting any type of response from host.'''
        message = BAD
        if not self.connected:
            print("This host is no longer connected.")
        else:
            message = self.sock.receive()
            if message == BAD:
                self.disconnect()
        return message

    def disconnect(self):
        self.connected = False
        self.sock.close()
        print(f"{self.name} has disconnected")
    
    def connnect(self):
        self.connected = True
        print(f"{self.name} has connected.")

    def is_connected(self):
        rlist, _, _ = select.select([self.sock], [], [], 0)
        if rlist:
            try:
                data = self.sock.recv(1, MSG_PEEK)
                if data:
                    return False
            except Exception as e:
                return False
        return True

    def set_name(self) -> str:
        self.give("Enter a username: ", IN)
        self.name = self.receive()
        return self.name

    def __str__(self):
        return f"[{self.name}, {self.ip}]"

class Server:
    '''NOTE - .open must be called for the server to accecpt clients'''
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
        '''Must be called to allow clients to connect to a server.'''
        print("Server is now open.")
        self.accepting = True
        self.accept_clients()
        self.update_connected()
    
    @asynchronus
    def update_connected(self):
        while True:
            sleep(1)
            for host_index in range(len(self.hosts) - 1, -1, -1):
                host = self.hosts[host_index]
                if not host.is_connected():
                    self.hosts.pop(host_index)
                    host.disconnect()


    def close(self):
        print("Server is now closed")
        self.accepting = False

    def broadcast(self, message: str | object, flag: str = OUT):
        '''Sends a message to all hosts currently connected to the server.
        (careful with the flag on this one)'''
        for host in self.hosts:
            if host.connected:
                host.give(message, flag)

    @asynchronus
    def accept_clients(self):
        while True:
            host_socket, host_addr = self.server_socket.accept()
            if self.accepting:
                ip = host_addr[0]
                if ip in self._get_host_ips(): # put 'and False if you do not want unique connections'
                    host = self._get_host_by_ip(ip)
                    host.sock = host_socket # update to most current socket
                    host.connnect()
                    host.give(f"Welcome back {host.name}!")
                else:
                    self.setup_host(host_socket, host_addr)
    
    # @background_process
    # def broadcast_connected(self):
    #     while True:
    #         sleep(5)
    #         connected_hosts = ""
    #         for host in self.get_connected_hosts():
    #             connected_hosts += host.name + " "
    #         self.broadcast(connected_hosts.rstrip(), )

    def setup_host(self, host_socket: ClientSocket, host_addr: tuple[str, int]):
        host = Host(host_socket, host_addr)
        while host.set_name() in self._get_host_names():
            host.sock.give("That name is taken!")
        if host.name == BAD:
            print("A Host failed to connect")
        else:
            host.connnect()
            self.hosts.append(host)
            host.give(f"Welcome {host.name}!")
    
    def get_connected_hosts(self):
        return [host for host in self.hosts if host.connected]
    
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