import os
import random
import sys
import time
import curses


class ArrowMazeGame:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        # Уменьшим размер поля, чтобы точно влезло в стандартное окно консоли (80x25)
        self.height = 20
        self.width = 40

        # Проверка размера экрана
        max_y, max_x = stdscr.getmaxyx()
        if max_y < self.height + 5 or max_x < self.width + 2:
            raise Exception(
                f"Console window too small! Need at least {self.width + 2}x{self.height + 5}, got {max_x}x{max_y}")

        self.player_pos = [1, 1]
        self.maze = []
        self.arrows = []
        self.score = 0
        self.total_arrows = 0
        self.game_over = False
        self.win = False

        # Настройка курсора (скрыть его)
        curses.curs_set(0)

        # Инициализация цветов (с проверкой поддержки)
        if curses.has_colors():
            curses.start_color()
            # Пары цветов: (номер, цвет_текста, цвет_фона)
            curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)  # Стены
            curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Игрок
            curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Стрелки
            curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)  # Текст
            self.use_colors = True
        else:
            self.use_colors = False

        self.generate_maze()
        self.place_arrows()
        self.total_arrows = len(self.arrows)

    def generate_maze(self):
        """Генерирует простой лабиринт со стенами"""
        self.maze = [[' ' for _ in range(self.width)] for _ in range(self.height)]

        # Границы
        for y in range(self.height):
            for x in range(self.width):
                if y == 0 or y == self.height - 1 or x == 0 or x == self.width - 1:
                    self.maze[y][x] = '#'

        # Случайные внутренние стены (немного меньше, чтобы было проще ходить)
        for _ in range(int(self.height * self.width * 0.1)):
            y = random.randint(1, self.height - 2)
            x = random.randint(1, self.width - 2)
            if [y, x] != self.player_pos:
                self.maze[y][x] = '#'

    def place_arrows(self):
        """Размещает стрелки в свободных клетках"""
        arrow_symbols = ['^', 'v', '<', '>']
        placed = 0
        attempts = 0
        target_arrows = 10

        while placed < target_arrows and attempts < 1000:
            y = random.randint(1, self.height - 2)
            x = random.randint(1, self.width - 2)

            # Проверяем, что клетка свободна и не занята игроком
            if self.maze[y][x] == ' ' and [y, x] != self.player_pos:
                # Проверяем, нет ли уже стрелки здесь
                if not any(a[0] == y and a[1] == x for a in self.arrows):
                    symbol = random.choice(arrow_symbols)
                    self.arrows.append([y, x, symbol])
                    placed += 1
            attempts += 1

    def safe_addch(self, y, x, char, color_pair=0):
        """Безопасная отрисовка символа с проверкой границ"""
        max_y, max_x = self.stdscr.getmaxyx()
        if 0 <= y < max_y and 0 <= x < max_x:
            try:
                if self.use_colors and color_pair > 0:
                    self.stdscr.addch(y, x, char, curses.color_pair(color_pair))
                else:
                    self.stdscr.addch(y, x, char)
            except curses.error:
                pass  # Игнорируем ошибки отрисовки

    def draw(self):
        """Отрисовка игры"""
        self.stdscr.clear()

        # Рисуем лабиринт
        for y in range(self.height):
            for x in range(self.width):
                char = self.maze[y][x]
                if char == '#':
                    self.safe_addch(y, x, '#', 1)
                else:
                    self.safe_addch(y, x, ' ')

        # Рисуем стрелки
        for arrow in self.arrows:
            y, x, symbol = arrow
            self.safe_addch(y, x, symbol, 3)

        # Рисуем игрока
        py, px = self.player_pos
        self.safe_addch(py, px, '@', 2)

        # Интерфейс (рисуем ниже поля)
        status = f" Score: {self.score}/{self.total_arrows} "
        self.safe_addstr(self.height + 1, 0, status, 4)

        if self.win:
            msg = " YOU WIN! Press 'q' to quit. "
            self.safe_addstr(self.height + 2, 0, msg, 2)
        elif self.game_over:
            msg = " GAME OVER! Press 'q' to quit. "
            self.safe_addstr(self.height + 2, 0, msg, 1)
        else:
            hint = " Use WASD or Arrows to move. Free all arrows! "
            self.safe_addstr(self.height + 3, 0, hint, 4)

        self.stdscr.refresh()

    def safe_addstr(self, y, x, text, color_pair=0):
        """Безопасная отрисовка строки"""
        max_y, max_x = self.stdscr.getmaxyx()
        if 0 <= y < max_y:
            try:
                if self.use_colors and color_pair > 0:
                    self.stdscr.addstr(y, x, text, curses.color_pair(color_pair))
                else:
                    self.stdscr.addstr(y, x, text)
            except curses.error:
                pass

    def move_player(self, dy, dx):
        """Логика движения игрока"""
        if self.win or self.game_over:
            return

        new_y = self.player_pos[0] + dy
        new_x = self.player_pos[1] + dx

        # Проверка на выход за границы массива лабиринта
        if new_y < 0 or new_y >= self.height or new_x < 0 or new_x >= self.width:
            return

        # Проверка на стены
        if self.maze[new_y][new_x] == '#':
            return

            # Обновляем позицию
        self.player_pos = [new_y, new_x]

        # Проверка на сбор стрелки
        # Используем копию списка, чтобы безопасно удалять
        for i in range(len(self.arrows) - 1, -1, -1):
            arrow = self.arrows[i]
            ay, ax, _ = arrow
            if ay == new_y and ax == new_x:
                # Освобождаем стрелку
                self.arrows.pop(i)
                self.score += 1
                break

        # Проверка победы
        if self.score == self.total_arrows:
            self.win = True

    def run(self):
        """Основной цикл игры"""
        self.stdscr.nodelay(True)  # Не ждать ввода

        while True:
            self.draw()

            try:
                key = self.stdscr.getch()
            except:
                key = -1

            if key == ord('q') or key == ord('Q'):
                break

            if key == curses.KEY_UP or key == ord('w') or key == ord('W'):
                self.move_player(-1, 0)
            elif key == curses.KEY_DOWN or key == ord('s') or key == ord('S'):
                self.move_player(1, 0)
            elif key == curses.KEY_LEFT or key == ord('a') or key == ord('A'):
                self.move_player(0, -1)
            elif key == curses.KEY_RIGHT or key == ord('d') or key == ord('D'):
                self.move_player(0, 1)

            if self.win:
                time.sleep(0.1)


def main(stdscr):
    game = ArrowMazeGame(stdscr)
    game.run()


if __name__ == "__main__":
    # Важно: для Windows иногда нужно установить локаль, чтобы корректно работали цвета
    if sys.platform == 'win32':
        os.system('')  # Включает обработку ANSI escape sequences в новых Windows 10/11

    try:
        curses.wrapper(main)
    except Exception as e:
        print(f"Произошла ошибка при запуске игры: {e}")
        input("Нажмите Enter, чтобы выйти...")