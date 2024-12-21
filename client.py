from .consts import IN, BAD, CLEAR, BG, CHAT
from .sockets import ClientSocket
from abc import ABC, abstractmethod
import asyncio
from threading import Thread
import select
from _socket import MSG_PEEK
from time import sleep, asctime
from random import randint

LOG_PATH = "client_debug_log.txt"
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
        self.eventloop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.eventloop)

    def disconnect(self, e: str = "You have been disconnected"):
        self.server.close()
        self.connected = False
        add_to_log(e)
    
    def connect(self):
        self.eventloop.run_until_complete(self._connect())
        if self.connected:
            updating = Thread(target=self.update_connected)
            receiving = Thread(target=self.receive_messages)
            updating.start()
            receiving.start()
            updating.join()
            receiving.join()
                
    async def _connect(self, timeout: int = 1):
        try:
            self.server = ClientSocket()
            connecting = asyncio.to_thread(self.server.connect, self.server_addr)
            await asyncio.wait_for(connecting, timeout)
            self.connected = True
        except asyncio.TimeoutError:
            add_to_log("Timeout Error: Server may currently be closed.")
        except Exception as e:
            add_to_log(f"Invalid Server Address: {e}")

    def update_connected(self):
        while self.connected:
            sleep(1)
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