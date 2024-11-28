from dataclasses import dataclass
from socket import socket, getdefaulttimeout
from time import sleep
from .utils import background_process
from .consts import HEADER_LENGTH, ACK_SIZE, ACK, \
      OUT, IN, GOOD, BAD, CLEAR

@dataclass
class Data:
    data: bytes
    received: bool = False

    @background_process
    def start_timeout(self, timeout = 4):
        sleep(timeout)
        if not self.received:
            raise Exception("Data was sent, but not received.")

def make_header(data: bytes):
    header = str(len(data)).encode()
    header += b' ' * (HEADER_LENGTH - len(header))
    return Data(header)

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
    
class ClientSocket(socket):
    
    '''
    special socket used to abstract sending / receiving data and maintaining protocol'''
    def give(self, message: str, flag: str = OUT) -> str:
        '''
        Sends message and message header to client socket. 
        Optional IN flag parameter, if IN parameter is passed receive() must be called! 
        Returns BAD if an error occurs, otherwise returns GOOD.'''
        ret = GOOD
        try:
            if flag != OUT:
                print(f"sending flag ({'CLEAR' if flag == CLEAR else 'IN'})")
                ret = self.give(flag)
            data = Data(message.encode()) 
            header = make_header(data.data)
            # print("sending header")
            if self._send(header):
                # print("sending data")
                self._send(data)
        except Exception as e:
            print(f"Something went wrong while sending a message: {e}")
            ret = BAD
        return ret

    def _send(self, data: Data) -> bool:
        '''
        sends encoded data, and waits for client acks, and marks data as received'''
        self.send(data.data)
        data.start_timeout()
        # print("waiting for ack")
        response = self.recv(ACK_SIZE)
        # print("ack received")
        if response:
            data.received = True
        return data.received

    def receive(self) -> str:
        '''
        handles receiving messages from the client's server and sends acks when messages are received and returns the message.
        (assumes first message is a header). When successful, method returns the message, otherwise returns BAD.'''
        ret = BAD
        try:
            header = self.recv(HEADER_LENGTH) # receives header with size of incoming message
            if header:
                message_len = int(header)
                # print(f"header size: {message_len}")
                # print(f"sending ack (header)")
                self.send(ACK)
                message = self.recv(message_len).decode() # receives actual message
                if message: # (could possibly be removed, doesnt assume that message will be received properly even if header is received.)
                    # print(f"sending ack ({message})")
                    self.send(ACK)
                    ret = message
        except Exception as e:
            print(f"something went wrong while receiving a message: {e}")
        return ret