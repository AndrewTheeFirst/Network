# FLG_IN = 2
# FLG_CLS = 4
# FLG_BG = 8

# MSG_FSIG = "\r\r"
# MSG_BAD = "\r\f\r\f"
# MSG_ACK = "\r\n\r\n"
# MSG_NUL = "\0"

IN = "0000" # tells client to send input
OUT = "0001" # mostly used as a placeholder
OK = "0010" # mostly used as a placeholder
BAD = "0011" # signals that something went wrong

CLEAR = "0100" # tells client to clear their console
BG = "0101" # signals that message is for background process
RENDER = "0110"
CHAT = "0111"

# HOST = "10.26.34.39" # laptop in dorm
# HOST = "10.26.7.26"
HOST = "192.168.1.184" # laptop at home
PORT = 5555