from .consts import IN, BAD, CLEAR
from .sockets import ClientSocket
from .utils import wclear, wprint, wread
from curses import window, initscr, echo, noecho

class Client:
    def __init__(self, window: window = None, host: str = "", port: int = 0):
        self.connected = False
        if not window:
            window = initscr()
        self.main_window = window
        
        if host and port:
            self.connect()
            
    def main_loop(self):
        while self.connected:
            message = self.server.receive()
            if message != BAD:
                self.process(message)
            else:
                self.disconnect()
                    
    def join_server(self):
        success = True
        self.server = ClientSocket()
        echo() # to see user input
        wprint(self.main_window, 1, 1, "Server IP: ")
        host = self.main_window.getstr().decode()
        wclear(self.main_window)
        wprint(self.main_window, 1, 1, "Server PORT: ")
        try:
            port = int(self.main_window.getstr().decode())
            self.connect(host, port)
        except Exception as e:
            wclear(self.main_window)
            wprint(self.main_window, 1, 1, f"Invalid Server Address: {e}")
            wprint(self.main_window, 2, 1, "Press any key to return.")
            noecho() # turn off see user input
            self.main_window.getch()
            wclear(self.main_window)
            success = False
        return success

    def connect(self, host: str, port: int):
            self.server_addr = (host, port)
            self.server.connect(self.server_addr)
            self.connected = True
            print("You are connected to the server.")

    def disconnect(self):
        self.server.close()
        self.connected = False
        print("You have been disconnected from the server.")
        
    def process(self, message: str):
        if message == IN:
            actual_message = self.server.receive()
            wread(self.main_window, actual_message)
            response = self.main_window.getstr().decode()
            self.server.give(response)
        elif message == CLEAR:
            actual_message = self.server.receive()
            wclear(self.main_window)
            wprint(self.main_window, actual_message)
        else:
            wprint(self.main_window, message)
            
if __name__ == "__main__":
    client = Client()
    client.main_loop()