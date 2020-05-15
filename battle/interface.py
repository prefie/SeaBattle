"""Модуль реализует интерфейс игры «Морской бой»"""

import curses
import sys


class Interface:
    def __init__(self, game):
        """Создание интерфейса пользователя"""
        self.game = game
        self.dx = game.player.field.size_x * 2 + 1
        self.dy = game.player.field.size_y + 2
        self.window = curses.initscr()
        height, width = self.window.getmaxyx()
        if height < self.dy + 2 or width < 1 + 2 * self.dx + 5:
            print('Расширьте окно консоли и запустите приложение заново')
            sys.exit(1)
        if self.game.size_y < 2 or self.game.size_x < 4:
            print('Минимальная высота - 2, ширина - 4 ')
            sys.exit(1)
        curses.noecho()  # Нельзя писать
        curses.curs_set(0)  # Не видно курсор
        curses.mousemask(1)
        curses.start_color()
        try:
            self.win_player = curses.newwin(self.dy, self.dx, 1, 1)
            self.win_bot = curses.newwin(
                self.dy, self.dx, 1, 1 + self.dx + 5)
            self.win_end = None
        except Exception:
            print('Расширьте окно консоли и запустите приложение заново')
            sys.exit(1)
        self.win_player.keypad(True)
        self.win_bot.keypad(True)
        self.win_player.box()
        self.win_bot.box()

        self._start()

    def _start(self):
        self.win_bot.clear()
        self.win_player.clear()
        for i in range(1, self.dx - 1):
            for j in range(1, self.dy - 1):
                if i % 2 == 0:
                    self.win_player.addstr(j, i, '|')
                    self.win_bot.addstr(j, i, '|')
                elif j != self.dy - 1 - 1:  # У посл. строчки нет подчёркиваний
                    self.win_player.addstr(j, i, '_')
                    self.win_bot.addstr(j, i, '_')
        self.window.addstr(self.dy + 1, (1 + self.dx) // 2 - 5, "Ваше поле")
        self.window.addstr(self.dy + 1, 5 + self.dx + (1 + self.dx) // 2 - 7, "Поле противника")
        self.window.refresh()
        self.win_player.refresh()
        self.win_bot.refresh()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        self.update()

    def update(self):
        """Обновление картинки (окон с полями)"""

        for i in self.game.player.field.cells:
            self.win_player.addstr(i.y + 1, (i.x + 1) * 2 - 1, '#')

        self._print_result_shot(self.game.player.field.shots,
                                self.win_player)
        self._print_result_shot(self.game.bot.field.shots,
                                self.win_bot)

        curses.curs_set(0)
        self.win_player.box()
        self.win_bot.box()
        self.window.refresh()
        self.win_player.refresh()
        self.win_bot.refresh()

    @staticmethod
    def _print_result_shot(shots, win):
        for i in shots:
            if shots[i]:
                win.addstr(
                    i.y + 1, (i.x + 1) * 2 - 1, 'X', curses.color_pair(1))
            else:
                win.addstr(
                    i.y + 1, (i.x + 1) * 2 - 1, 'o', curses.color_pair(2))
        win.refresh()

    def click_user(self):
        """Обработка клика пользователя.
        Возвращает координаты относительно игрового поля"""
        self.update()
        key = self.win_bot.getch()
        if key == ord('q'):
            curses.endwin()
            print('Вы вышли из игры.')
            sys.exit(0)
        if key == ord('r'):
            self.game.restart()
            self._start()
        if key == curses.KEY_MOUSE:
            _, mx, my, _, _ = curses.getmouse()
            if my - 1 > 0 and self.dx + 5 < mx < 2 * self.dx + 5 \
                    and my < self.dy:
                if mx % 2 == 0:
                    x = (mx - self.dx - 5 - 1 + 1) // 2 - 1
                    y = my - 1 - 1
                    return x, y
        return self.click_user()

    def the_end(self, player_win):
        """Окно конца игры"""
        self._clear()
        winner = 'Игрок' if player_win else 'Искусственный интеллект'
        while True:
            curses.curs_set(0)
            y, x = self.window.getmaxyx()
            try:
                self.win_end = curses.newwin(3, (10+len(winner)),
                                             y // 2 - 1, x // 2 - (10+len(winner))//2)
                self.win_end.addstr(1, 1, f'Победил {winner}')
            except Exception:
                print('Вы вышли из игры.')
                sys.exit(1)
            self.win_end.box()
            self.win_end.refresh()
            key = self.win_bot.getch()
            if key == ord('q'):
                curses.endwin()
                print('Вы вышли из игры.')
                sys.exit(0)
            if key == ord('r'):
                self._clear()
                self.game.restart()
                self._start()
                break

    def _clear(self):
        self.window.erase()
        self.window.refresh()
