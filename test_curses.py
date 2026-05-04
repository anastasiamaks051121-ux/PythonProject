import curses

def main(stdscr):
    stdscr.clear()
    stdscr.addstr(0, 0, "HELLO! If you see this, curses works.")
    stdscr.addstr(1, 0, "Press any key to exit...")
    stdscr.refresh()
    stdscr.getch()

curses.wrapper(main)