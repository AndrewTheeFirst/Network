from socket import socket, getdefaulttimeout
from threading import Thread
from .consts import *
from dataclasses import dataclass

ACK = "RECEIVED".encode()
ACK_SIZE = len(ACK)
HEADER_LENGTH = 8
NULL_MESSAGE = "\0"

class ServerSocket(socket):
    '''
    initializes a TCP IPv4 server socket'''

    def accept(self):
        """accept() -> (ClientSocket, address info)

        Wait for an incoming connection. Return a new ClientSocket
        representing the connection, and the address of the client.
        """
        fd, addr = self._accept()
        sock = ClientSocket(self.family, self.type, self.proto, fileno=fd)
        if getdefaulttimeout() is None and self.gettimeout():
            sock.setblocking(True)
        return sock, addr

@dataclass
class Packet:
    received: bool = False

class ClientSocket(socket):
    
    '''
    Special socket used to abstract sending / receiving data and maintaining protocol'''

    def crecv(self) -> str:
        '''
        Receive a message from a client / server.\n
        When successful, method returns the message, otherwise returns consts.BAD.'''
        ret = BAD
        try:
            header = super().recv(HEADER_LENGTH)
            if header.isdigit():
                super().send(ACK)
                message = super().recv(int(header)).decode()
                if message:
                    super().send(ACK)
                    ret = "" if message == NULL_MESSAGE else message
        except Exception as e:
            print(f"something went wrong while receiving a message: {e}")
        return ret

    @staticmethod    
    def _make_header(data: bytes):
        header = str(len(data)).encode()
        header += b' ' * (HEADER_LENGTH - len(header))
        return header

    def _receive_ack(self, packet: Packet):
        self.recv(ACK_SIZE)
        packet.received = True

    def _send_aspacket(self, data: bytes, /, timeout = 2, tries = 3) -> bool:
        packet = Packet()
        super().send(data)
        t = Thread(self._receive_ack(), packet)
        t.start()
        for _ in range(tries - 1):
            t.join(timeout)
            if not t.is_alive():
                break
            super().send(data)
        if t.is_alive():
            raise Exception("Connection Error: Packet was not ACKED in time.")
        if not packet.received:
            raise Exception("Connection Error: The server could not be reached.")

    def _send_asdatagram(self, message: str):
        data = message.encode()
        header = ClientSocket._make_header(data)
        self._send_aspacket(header)
        self._send_aspacket(data)

    def csend(self, message: str, flag: str = None) -> str:
        '''
        Send a message to a client / server.\n
        Returns consts.BAD if an error occurs, otherwise returns consts.OK.'''
        message = NULL_MESSAGE if message == "" else message
        try:
            if flag:
                self._send_asdatagram(flag)
            self._send_asdatagram(message)
        except Exception as e:
            return BAD
        return OK
