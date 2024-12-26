from .consts import IN, BAD, CLEAR, BG, CHAT
from .sockets import ClientSocket
from abc import ABC, abstractmethod
from threading import Thread
import select
from _socket import MSG_PEEK
from time import sleep, asctime
from random import randint

LOG_PATH = "debug/client_debug_log.txt"
ID = randint(1, 100)
def add_to_log(message: str):
    with open(LOG_PATH, 'a') as log:
        log.write(f"{asctime()} | PID {ID}: {message}\n")

class BaseClient(ABC):
    def __init__(self):
        super().__init__()
        self.connected = False
        self.server = ClientSocket()
        self.server_addr = ()

    def disconnect(self, e: str = "You have been disconnected"):
        self.server.close()
        self.connected = False
        add_to_log(e)
    
    def connect(self):
        self._connect()
        if self.connected:
            receiving = Thread(target=self.receive_messages)
            updating = Thread(target=self.update_connected)
            receiving.start()
            updating.start()
            receiving.join()
            updating.join()
                
    def _connect(self):
        try:
            self.server = ClientSocket()
            self.server.connect(self.server_addr)
            if self.server.recv(1, MSG_PEEK):
                self.connected = True
        except TimeoutError:
            add_to_log("Timeout Error: Server may currently be closed.")
        except Exception as e:
            add_to_log(f"Invalid Server Address: {e}")

    def update_connected(self):
        while self.connected:
            sleep(1)
            if not self.server or self.server.fileno() == -1:
                self.disconnect("Something went wrong.")
                break
            rlist, _, _ = select.select([self.server], [], [], 0)
            if rlist:
                try:
                    data = self.server.recv(1, MSG_PEEK)
                    if not data:
                        self.disconnect(f"A Network Error occured.")
                except Exception as e:
                    self.disconnect(f"Server Error: {e}")

    def receive_messages(self):
        while self.connected:
            try:
                message = self.server.crecv()
                if not message or message == BAD:
                    self.disconnect()
                else:
                    self.process(message)
            except Exception as e:
                add_to_log(e)

    @abstractmethod
    def process(self, message: str):
        ...