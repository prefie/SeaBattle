"""Модуль реализует интерфейс игры «Морской бой»"""

import curses
import sys


class Interface:
    def __init__(self, game):
        self.game = game
        self.dx = game.player.field.size_x * 2 + 1
        self.dy = game.player.field.size_y + 2
        window = curses.initscr()
        height, width = window.getmaxyx()
        if height < self.dy or width < 1 + 2 * self.dx + 5:
            print('Расширьте окно консоли и запустите приложение заново')
            sys.exit(1)
        curses.noecho()  # Нельзя писать
        curses.curs_set(0)  # Не видно курсор
        curses.mousemask(1)
        curses.start_color()
        try:
            self.win_player = curses.newwin(self.dy, self.dx, 1, 1)
            self.win_bot = curses.newwin(
                self.dy, self.dx, 1, 1 + self.dx + 5)
        except Exception:
            print('Расширьте окно консоли и запустите приложение заново')
            sys.exit(1)
        self.win_player.keypad(1)
        self.win_bot.keypad(1)
        self.win_player.box()
        self.win_bot.box()
        for i in range(1, self.dx - 1):
            for j in range(1, self.dy - 1):
                if i % 2 == 0:
                    self.win_player.addstr(j, i, '|')
                    self.win_bot.addstr(j, i, '|')
                elif j != self.dy - 1 - 1:  # У посл. строчки нет подчёркиваний
                    self.win_player.addstr(j, i, '_')
                    self.win_bot.addstr(j, i, '_')
        self.win_player.refresh()
        self.win_bot.refresh()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        self.update()

    def update(self):
        """Обновление картинки (окон с полями)"""

        for i in self.game.player.field.cells:
            self.win_player.addstr(i.y + 1, (i.x + 1) * 2 - 1, '#')

        for i in self.game.player.field.shots:
            if self.game.player.field.shots[i]:
                self.win_player.addstr(
                    i.y + 1, (i.x + 1) * 2 - 1, 'X', curses.color_pair(1))
            else:
                self.win_player.addstr(
                    i.y + 1, (i.x + 1) * 2 - 1, 'o', curses.color_pair(2))
        self.win_player.refresh()

        for i in self.game.bot.field.shots:
            if self.game.bot.field.shots[i]:
                self.win_bot.addstr(
                    i.y + 1, (i.x + 1) * 2 - 1, 'X', curses.color_pair(1))
            else:
                self.win_bot.addstr(
                    i.y + 1, (i.x + 1) * 2 - 1, 'o', curses.color_pair(2))
        self.win_bot.refresh()

        curses.curs_set(0)
        self.win_player.box()
        self.win_bot.box()
        self.win_player.refresh()
        self.win_bot.refresh()

    def click_user(self):
        self.update()
        key = self.win_bot.getch()
        if key == ord('q'):
            curses.endwin()
            print('Вы вышли из игры.')
            sys.exit(0)
        if key == ord('r'):
            """restart"""
            pass
        if key == curses.KEY_MOUSE:
            _, mx, my, _, _ = curses.getmouse()
            if my - 1 > 0 and self.dx + 5 < mx < 2 * self.dx + 5 \
                    and my < self.dy:
                if mx % 2 == 0:
                    x = (mx - self.dx - 5 - 1 + 1) // 2 - 1
                    y = my - 1 - 1
                    return x, y
        return self.click_user()
