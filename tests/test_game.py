#!/usr/bin/env python3

import unittest
from battle.game import Game
from battle.logic import *
from battle.botAI import BotAI


class Tests(unittest.TestCase):
    def test_count_cells_random_placement(self):
        field = Field(10, 10, 4)
        field.random_placement_ships()
        self.assertEqual(20, len(field.cells))

    def test_count_ships_random_placement(self):
        field = Field(20, 20, 5)
        field.random_placement_ships()
        self.assertEqual(15, len(field.ships))

    def test_shot(self):
        field = Field(10, 10, 4)
        field.add_ship([Cell(0, 0), Cell(0, 1)])

        cell = Cell(0, 1)
        field.shot(cell)

        self.assertTrue(field.shots[cell])

    def test_random_shot_level_1(self):
        field = Field(10, 20, 5)
        cell = BotAI.shot_level_1(field)
        self.assertTrue(cell == ResultShot.MISS or
                        cell == ResultShot.HIT)
        self.assertTrue(len(field.shots) > 0)

    def test_start_game(self):
        game = Game(10, 10, 4, 1)
        game.start()

        self.assertEqual(20, len(game.player.field.cells))
        self.assertEqual(20, len(game.bot.field.cells))

    def test_empty_game(self):
        game = Game(10, 10, 4, 1)
        print(game.player_is_win())
        self.assertTrue(game.player_is_win())

    def test_generation_ship_horizontal(self):
        field = Field(10, 10, 4)

        ship = field.generation_ship(4, Cell(8, 9), Direction.HORIZONTAL)
        ans = Ship([Cell(8, 9), Cell(9, 9), Cell(0, 9), Cell(1, 9)])
        self.assertEqual(ans, ship)

    def test_generation_ship_vertical(self):
        field = Field(10, 10, 4)

        ship = field.generation_ship(3, Cell(0, 9), Direction.VERTICAL)
        ans = Ship([Cell(0, 9), Cell(0, 0), Cell(0, 1)])
        self.assertEqual(ans, ship)

    """def test_player_move(self):
        game = Game(10, 10, 4, 1)

        ship =\
            game.bot.field.generation_ship(4, Cell(0, 0), Direction.VERTICAL)
        game.bot.field.add_ship(ship)

        result = None
        for i in range(2, 6):
            result = battle.player_move(game, 28, i, 21, 12)
        self.assertEqual(Action.BREAK, result)"""

    """def test_bot_move(self):
        game = Game(10, 10, 4)

        game.start()
        battle.bot_move(game)
        self.assertTrue(len(game.player.field.shots) > 0)"""


if __name__ == '__main__':
    unittest.main()
