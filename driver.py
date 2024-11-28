from .client import Client
from .utils import wprint, wclear
import curses

class Driver:
    def __init__(self):
        self.main_window = curses.initscr()
        curses.noecho() # typed keys will not display keys onto the window
        curses.cbreak() # program will not wait for the enter key to be pressed to react to input
        if curses.has_colors:
            curses.start_color()
            self.init_colors()
        self.build_window()
        self.client = Client(self.game_area)

    def build_window(self):
        '''places windows and refreshes the '''
        self.main_window.noutrefresh()
        self.lines, self.cols = self.main_window.getmaxyx()
        self.header = self.make_header()
        self.footer = self.make_footer()
        self.game_area = self.make_game_area()

        curses.doupdate()
    
    def init_colors(self):
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        
    def make_header(self, refresh: bool = False):
        '''shows game title and any extra information'''
        text = "Phase Ten"
        header = curses.newwin(1, self.cols - 1, 0, 0)
        characters = len(text)
        middle = self.cols // 2 + 1
        start = middle - characters // 2
        header.addstr(0, start, text)
        header.noutrefresh()
        if refresh:
            header.refresh()
        return header

    def make_game_area(self, refresh: bool = False):
        '''main area for updating game graphics'''
        area_outline = curses.newwin(self.lines - 2, self.cols - 1, 1, 0)
        game_area = curses.newwin(self.lines - 4, self.cols - 5, 2, 2) # give 2 cols of space (cols smaller than lines)

        area_outline.box()
        # game_area.box() # just to see where the area is
        area_outline.noutrefresh()
        game_area.noutrefresh()
        if refresh:
            area_outline.refresh()
            game_area.refresh()
        return game_area
    
    def event_loop(self):
        while True:
            key = self.main_window.getkey().upper()
            match(key):
                case 'Q':
                    self.close()
                    break
                case 'C':
                    wclear(self.footer)
                    ret = self.client.join_server()
                    if ret:
                        self.client.main_loop()
                    self.footer = self.make_footer(True)
                case 'R':
                    self.close()
                    self.__init__()
    
    def make_footer(self, refresh: bool = False):
        '''shows controls and any extra information'''
        footer = curses.newwin(1, self.cols - 1, self.lines - 1, 0)
        text = "| Press Q to Quit | Press C to Connect to server | Press R to Reload Window |"
        footer.addstr(text)
        for label in ["Quit", "Connect", "Reload"]:
            footer.chgat(0, text.find(label) - 5, 1, curses.color_pair(1))
        footer.noutrefresh()
        if refresh:
            footer.refresh()
        return footer
    
    def confirm(self):
        pass

    def close(self):
        self.main_window.keypad(0)
        curses.echo() # reverses curses.noecho()
        curses.nocbreak() # reverses curses.cbreak()
        curses.endwin() # restores default terminal

