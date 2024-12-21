from socket import socket, getdefaulttimeout
from threading import Thread
from .consts import *

def make_header(data: bytes):
    header = str(len(data)).encode()
    header += b' ' * (HEADER_LENGTH - len(header))
    return header

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

    def crecv(self) -> str:
        '''
        handles receiving messages from the client's server and sends acks when messages are received and returns the message.
        (assumes first message is a header). When successful, method returns the message, otherwise returns BAD.'''
        ret = BAD
        try:
            header = super().recv(HEADER_LENGTH) # receives header with size of incoming message
            if header:
                message_len = int(header)
                # print(f"header size: {message_len}")
                # print(f"sending ack (header)")
                super().send(ACK)
                message = super().recv(message_len).decode() # receives actual message
                if message: # (could possibly be removed, doesnt assume that message will be received properly even if header is received.)
                    # print(f"sending ack ({message})")
                    super().send(ACK)
                    ret = "" if message == NULL_MESSAGE else message
        except Exception as e:
            print(f"something went wrong while receiving a message: {e}")
        return ret

    def csend(self, message: str, flag: str = OUT) -> str:
        '''
        Sends message and message header to client socket. 
        Optional IN flag parameter, if IN parameter is passed receive() must be called! 
        Returns BAD if an error occurs, otherwise returns GOOD.'''
        ret = GOOD
        message = NULL_MESSAGE if message == "" else message
        try:
            if flag != OUT:
                data = flag.encode()
                print(f"sending flag ({'CLEAR' if flag == CLEAR else 'IN'})")
                self.send_datagram(data) # i used to return the result here, but function no longer yields result
            data = message.encode()
            self.send_datagram(data)
        except Exception as e:
            print(f"Something went wrong while sending a message: {e}")
            ret = BAD
        return ret
    
    def send_datagram(self, data: bytes):
        header = make_header(data)
        self._send(header)
        self._send(data)

    def _send(self, data: bytes) -> bool:
        '''
        sends encoded data, and waits for client acks, and marks data as received'''
        super().send(data)
        receive_ack = Thread(target=super().recv, args=(ACK_SIZE,))
        receive_ack.start()
        receive_ack.join(2)
        for _ in range(2):
            if not receive_ack.is_alive():
                break
            super().send(data) # try to resend the data
        else:
            raise Exception("Connection Error: A sent packet was not ACKED in time.")