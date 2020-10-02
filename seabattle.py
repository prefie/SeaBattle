#!/usr/bin/env python3
"""Консольная версия игры «Морской бой»"""

import argparse
import sys
import _curses
from battle.game import Game
from battle.interface import Interface


def parse_args():
    """Разбор аргументов запуска"""
    parser = argparse.ArgumentParser(description='Seabattle game')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-l', '--load', action='store_true',
                       help='load a saved game')
    group.add_argument('-g', '--game', nargs=4, type=int,
                       metavar=('SIZE_Y', 'SIZE_X', 'MAX_SIZE_SHIP', 'LEVEL'),
                       help='creating a new game')
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

        interface = Interface(game)
    except ValueError as e:
        print('Такая конфигурация поля игры невозможна.', e, file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print('Файла сохранения нет или он некорректен.', e, file=sys.stderr)
        sys.exit(1)
    except _curses.error as e:
        print('Расширьте окно консоли и запустите приложение заново.', e, file=sys.stderr)
        sys.exit(1)

    if not args.load:
        game.start()

    interface.run()


if __name__ == '__main__':
    main()
