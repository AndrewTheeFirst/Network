IN = "0000" # tells client to send input
OUT = "0001" # mostly used as a placeholder
GOOD = "0010" # mostly used as a placeholder
BAD = "0011" # signals that something went wrong

CLEAR = "0100" # tells client to clear their console
BG = "0101" # signals that message is for background process
RENDER = "0110"
CHAT = "0111"

ACK = "RECEIVED".encode()
ACK_SIZE = len(ACK)
HEADER_LENGTH = 8

NULL_MESSAGE = "\0"

HOST = "10.26.34.39" # laptop in dorm
# HOST = "10.26.7.26"
# HOST = "192.168.1.184" # laptop at home
PORT = 5555