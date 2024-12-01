from .consts import IN, BAD, CLEAR, BG
from .sockets import ClientSocket
from .utils import wclear, wprint, wread, background_process
import curses
from curses import window
from time import sleep

class Client:
    def __init__(self, window: window = None, host: str = "", port: int = 0):
        self.connected = False
        if not window:
            window = curses.initscr()
        self.main_window = window
        if host and port:
            self.connect()
        

    def build_window(self):
        self.lines, self.cols = self.main_window.getmaxyx()
        self.beg_y, self.beg_x = self.main_window.getbegyx()
        self.main_window.noutrefresh()
        self.game_area = self.make_game_area()
        self.message_box = self.make_message_box()
        curses.doupdate()
            
    def make_game_area(self):
        outline = curses.newwin(self.lines - 3, self.cols, 0 + self.beg_y, 0 + self.beg_x)
        # outline.box()
        game_area = curses.newwin(self.lines - 5, self.cols - 4, 1 + self.beg_y, 2 + self.beg_x)
        # outline.noutrefresh()
        game_area.noutrefresh()

        return game_area

    def make_message_box(self):
        outline = curses.newwin(3, self.cols, self.lines - 3 + self.beg_y, 0 + self.beg_x)
        outline.box()
        message_box = curses.newwin(1, self.cols - 4, self.lines - 2 + self.beg_y, 2 + self.beg_x)
        outline.noutrefresh()
        message_box.noutrefresh()

        return message_box

    def main_loop(self):
        while self.connected:
            message = self.server.receive()
            if message == BAD:
                self.disconnect()
            # elif message == BG:
            #     self.update()
            else:
                self.process(message)
    
    def update(self):
        pass
                              
    def join_server(self):
        success = True
        self.server = ClientSocket()
        curses.echo() # to see user input
        wprint(self.message_box, "Server IP: ")
        host = self.message_box.getstr().decode()
        wclear(self.message_box)
        wprint(self.message_box, "Server PORT: ")
        try:
            port = int(self.message_box.getstr().decode())
            self.connect(host, port)
        except Exception as e:
            wclear(self.message_box)
            wprint(self.message_box, f"Invalid Server Address: {e}")
            sleep(2)
            wclear(self.message_box)
            wprint(self.message_box, "Press any key to return.")
            curses.noecho() # turn off see user input
            self.message_box.getch()
            wclear(self.message_box)
            success = False
        finally:
            wclear(self.message_box)
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
            wprint(self.message_box, actual_message)
            response = self.message_box.getstr().decode()
            self.server.give(response)
            wclear(self.message_box)
        elif message == CLEAR:
            actual_message = self.server.receive()
            wclear(self.game_area)
            wprint(self.game_area, actual_message)
        else:
            wprint(self.game_area, message)
            
if __name__ == "__main__":
    client = Client()
    client.main_loop()