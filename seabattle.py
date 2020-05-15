#!/usr/bin/env python3
"""Консольная версия игры «Морской бой»"""

import argparse
from battle.game import Game
from battle.interface import Interface


def parse_args():
    """Разбор аргументов запуска"""
    parser = argparse.ArgumentParser(description='Seabattle game')
    parser.add_argument('height', type=int, help='Height')
    parser.add_argument('width', type=int, help='Width')
    parser.add_argument('max_size_ship', type=int, help='Max_size_ship')
    parser.add_argument('level', type=int, help='Level')

    return parser.parse_args()


def main():
    """Точка входа в приложение"""
    args = parse_args()

    game = Game(args.width, args.height, args.max_size_ship, args.level)
    interface = Interface(game)
    game.start()

    while True:
        interface.update()

        if game.player_is_win() is not None:
            interface.the_end(game.player_is_win)

        if game.first_player_current:
            game.shot(interface.click_user())
        else:
            game.shot()


if __name__ == '__main__':
    main()
