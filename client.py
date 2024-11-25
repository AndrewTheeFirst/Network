from consts import HOST, PORT, IN, BAD, CLEAR
from socket import AF_INET, SOCK_STREAM
from utils import ClientSocket
from os import name as os_name, system

def clear():
    '''clears the console / terminal'''
    if os_name == "nt":
        system("cls")
    else:
        print("\x1b[2J\x1b[H", end="")

class Client:
    def __init__(self):
        self.server = ClientSocket(AF_INET, SOCK_STREAM)
        self.server_addr = (HOST, PORT)
        self.connect()
        
    def main_loop(self):
        while self.connected:
            message = self.server.receive()
            if message != BAD:
                self.process(message)
            else:
                self.disconnect()
                    
    def connect(self):
        self.server.connect(self.server_addr)
        self.connected = True
        print("You are connected to the server.")
    
    def disconnect(self):
        self.server.close()
        self.connected = False
        print("You have been disconnected from the server.")
        
    def process(self, message: str):
            if message == IN:
                prompt = self.server.receive()
                response = input(prompt)
                self.server.give(response)
            elif message == CLEAR:
                clear()
            else:
                print(message, end = "")
            
if __name__ == "__main__":
    client = Client()
    client.main_loop()