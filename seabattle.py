#!/usr/bin/env python3
"""Консольная версия игры «Морской бой»"""

import argparse
from battle.game import Game
from battle.interface import Interface


def parse_args():
    """Разбор аргументов запуска"""
    parser = argparse.ArgumentParser(description='Seabattle game')

    parser.add_argument('-l', '--load', action='store_true')
    parser.add_argument('-g', '--game', nargs=4, type=int, metavar=('SIZE_Y', 'SIZE_X', 'MAX_SIZE_SHIP', 'LEVEL'))
    args = parser.parse_args()
    if args.game is None and not args.load:
        return parser.parse_args(['-h'])
    return parser.parse_args()


def main():
    """Точка входа в приложение"""
    args = parse_args()

    try:
        if args.load:
            game = Game.load_game()
        else:
            height, width, max_size_ship, level = args.game
            game = Game(width, height, max_size_ship, level)
    except ValueError:
        print('Невозможная расстановка с таким значением максимальной длины корабля.')
        return
    except Exception:
        print('Файла сохранения нет или он некорректен.')
        return

    interface = Interface(game)
    if not args.load:
        game.start()

    while True:
        interface.update()

        if game.player_is_win() is not None:
            interface.the_end(game.player_is_win())

        if game.first_player_current:
            game.shot(interface.click_user())
        else:
            game.shot()


if __name__ == '__main__':
    main()
