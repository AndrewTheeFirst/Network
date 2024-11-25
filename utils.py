from threading import Thread
from typing import Callable
from dataclasses import dataclass
from socket import socket, \
    getdefaulttimeout, \
        AF_INET, SOCK_STREAM
from consts import HEADER_LENGTH, ACK_SIZE, ACK, \
      OUT, IN, GOOD, BAD

def background_process(func: Callable) -> Callable:
    '''aync function decorator'''
    def wrapper(*args):
        t = Thread(target = func, args = args)
        t.start()
    return wrapper

@dataclass
class Data:
    data: bytes
    received: bool = False

def make_header(data: bytes):
    header = str(len(data)).encode()
    header += b' ' * (HEADER_LENGTH - len(header))
    return Data(header)

class ServerSocket(socket):
    '''
    initializes a IPv4 server socket that uses TCP'''
    def __init__(self):
        super().__init__(AF_INET, SOCK_STREAM)

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
    
class ClientSocket(socket):
    '''
    special socket used to abstract sending / receiving data and maintaining protocol'''
    def give(self, message: str, flag: str = OUT) -> str:
        '''
        Sends message and message header to client socket. 
        Optional IN flag parameter, if IN parameter is passed receive() must be called! Returns BAD if an error occurs, otherwise returns GOOD.'''
        try:
            if flag == IN:
                # print("sending flag")
                self.give(flag)
            data = Data(message.encode()) 
            header = make_header(data.data)
            # print("sending header")
            if self._send(header):
                # print("sending data")
                self._send(data)
            return GOOD
        except Exception as e:
            print(f"Something went wrong while sending a message: {e}")
            return BAD

    def _send(self, data: Data) -> bool:
        '''
        sends encoded data, and waits for client acks, and marks data as received'''
        self.send(data.data)
        response = self.recv(ACK_SIZE)
        if response:
            data.received = True
        return data.received
  
    def receive(self) -> str:
        '''
        handles receiving messages from the client's server and sends acks when messages are received and returns the message. (assumes first message is a header). When successful, method returns the message, otherwise returns BAD.'''
        try:
            header = self.recv(HEADER_LENGTH) # receives header with size of incoming message
            if not header:
                return BAD
            message_len = int(header)
            # print(f"header size: {message_len}")
            # print("sending ack")
            self.send(ACK)
            message = self.recv(message_len).decode() # receives actual message
            if not message: # (could possibly be removed, doesnt assume that message will be received properly even if header is received.)
                return BAD
            # print("sending ack")
            self.send(ACK)
            return message
        except Exception as e:
            print(f"something went wrong while receiving a message: {e}")
            return BAD