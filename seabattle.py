#!/usr/bin/env python3
"""Консольная версия игры «Морской бой»"""

import sys
from battle.game import Game
from battle.interface import Interface

ERROR_EXCEPTION = 1


def main():
    """Точка входа в приложение"""
    if (len(sys.argv) > 1 and
            (sys.argv[1] == '--help' or sys.argv[1] == '-h')):
        print('''Используйте: seabattle.py [height] [width] [max_size_ship]''')
        sys.exit(0)

    if len(sys.argv) < 5:
        print('Некорректный запуск приложения. Введите seabattle.py --help')
        sys.exit(ERROR_EXCEPTION)

    try:
        height = int(sys.argv[1])
        width = int(sys.argv[2])
        max_size_ship = int(sys.argv[3])
        level = int(sys.argv[4])
    except Exception:
        print('Некорректный запуск приложения. Введите seabattle.py --help')
        sys.exit(ERROR_EXCEPTION)

    game = Game(width, height, max_size_ship, level)
    interface = Interface(game)
    game.start()

    while True:
        interface.update()

        if game.player_is_win() is not None:
            break

        if game.first_player_current:
            game.shot(interface.click_user())
        else:
            game.shot()

    print('Вин игрок' if game.player_is_win() else 'Вин тачка')


if __name__ == '__main__':
    main()
