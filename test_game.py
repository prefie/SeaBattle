#!/usr/bin/env python3

import unittest
from battle.game import Direction, Cell, Ship, Field, Game
from battle.botAI import BotAI
from copy import deepcopy


class FieldTest(unittest.TestCase):

    def test_load_bad(self):
        with self.assertRaises(ValueError):
            Field.fromstr('1;1;1;;;')

        with self.assertRaises(ValueError):
            Field.fromstr(';;;;;')

        with self.assertRaises(ValueError):
            Field.fromstr('10;10;4;33')

        with self.assertRaises(ValueError):
            Field.fromstr('4;4;1;;2;')

        with self.assertRaises(ValueError):
            Field.fromstr('10;10;4;;;2,1.True:2,1')

    def test_init_field(self):
        field = Field(5, 5, 2)
        self.assertTrue(field.is_empty())
        field.random_placement_ships()
        self.assertFalse(field.is_empty())

    def test_init_bad(self):
        with self.assertRaises(ValueError):
            Field(10, 10, 10)

        with self.assertRaises(ValueError):
            Field(2, 2, 1)

        with self.assertRaises(ValueError):
            Field(15, 15, 20)

    def test_count_cells_random_placement(self):
        field = Field(10, 10, 4)
        self.assertTrue(field.is_empty())
        field.random_placement_ships()
        self.assertEqual(20, len(field.cells))

        field = Field(15, 15, 4)
        field.random_placement_ships()
        self.assertEqual(20, len(field.cells))

        field = Field(15, 15, 6)
        field.random_placement_ships()
        self.assertEqual(56, len(field.cells))

        field = Field(4, 4, 1)
        field.random_placement_ships()
        self.assertEqual(1, len(field.cells))

        field = Field(4, 4, 2)
        field.random_placement_ships()
        self.assertEqual(4, len(field.cells))

    def test_count_ships_random_placement(self):
        field = Field(20, 20, 5)
        self.assertTrue(field.is_empty())
        field.random_placement_ships()
        self.assertEqual(15, len(field._ships))

        field = Field(10, 10, 4)
        field.random_placement_ships()
        self.assertEqual(10, len(field._ships))

        field = Field(4, 4, 2)
        field.random_placement_ships()
        self.assertEqual(3, len(field._ships))

    def test_add_ship(self):
        field = Field(10, 10, 4)

        self.assertTrue(field.add_ship(Ship([Cell(0, 0)])))
        self.assertTrue(Cell(0, 0) in field.cells)
        self.assertTrue(len(field._ships) > 0)

        self.assertFalse(field.add_ship(Ship([Cell(0, 0)])))
        self.assertFalse(field.add_ship(Ship([Cell(9, 0), Cell(0, 0)])))

    def test_shot_field(self):
        field = Field(10, 10, 4)
        field.add_ship([Cell(0, 0), Cell(0, 1)])
        cell = Cell(0, 1)
        field.shot(Cell(0, 1))
        self.assertTrue(field.shots[cell])

        field = Field(4, 2, 1)
        field.add_ship([Cell(1, 1)])
        field.shot(cell)
        field.shot(Cell(1, 1))
        self.assertFalse(field.shots[cell])
        self.assertTrue(field.shots[Cell(1, 1)])

    def test_generation_ship_horizontal(self):
        field = Field(10, 10, 4)

        ship = field.generation_ship(2, Cell(0, 0), Direction.HORIZONTAL)
        ans = Ship([Cell(0, 0), Cell(1, 0)])
        self.assertEqual(ans, ship)

        ship = field.generation_ship(4, Cell(8, 9), Direction.HORIZONTAL)
        ans = Ship([Cell(8, 9), Cell(9, 9), Cell(0, 9), Cell(1, 9)])
        self.assertEqual(ans, ship)

        field.add_ship(ship)

        ship = field.generation_ship(1, Cell(8, 9), Direction.HORIZONTAL)
        self.assertIsNone(ship)

        ship = field.generation_ship(3, Cell(6, 9), Direction.HORIZONTAL)
        self.assertIsNone(ship)

    def test_generation_ship_vertical(self):
        field = Field(10, 10, 4)

        ship = field.generation_ship(2, Cell(0, 0), Direction.VERTICAL)
        ans = Ship([Cell(0, 0), Cell(0, 1)])
        self.assertEqual(ans, ship)

        ship = field.generation_ship(3, Cell(0, 9), Direction.VERTICAL)
        ans = Ship([Cell(0, 9), Cell(0, 0), Cell(0, 1)])
        self.assertEqual(ans, ship)

        field.add_ship(ship)

        ship = field.generation_ship(1, Cell(0, 9), Direction.VERTICAL)
        self.assertIsNone(ship)

        ship = field.generation_ship(3, Cell(0, 7), Direction.VERTICAL)
        self.assertIsNone(ship)

    def test_field_fromstr(self):
        field = Field(10, 10, 4)
        self.assertEqual(field, Field.fromstr(str(field)))

        field.random_placement_ships()
        field.shot(Cell(1, 0))
        self.assertEqual(field, Field.fromstr(str(field)))

        field = Field(15, 15, 5)
        for i in range(15):
            field.shot(i, i)

        self.assertEqual(field, Field.fromstr(str(field)))


class GameTest(unittest.TestCase):

    def test_init_game(self):
        game = Game(10, 10, 4, 2)
        self.assertTrue(game.player_field.is_empty())
        self.assertTrue(game.bot_field.is_empty())
        self.assertTrue(game.is_player_win())

    def test_init_bad(self):
        with self.assertRaises(ValueError):
            Game(1, 1, 1, 1)

        with self.assertRaises(ValueError):
            Game(10, 10, 5, 2)

    def test_start_game(self):
        game = Game(10, 10, 4, 1)

        self.assertEqual(0, len(game.player_field.cells))
        self.assertEqual(0, len(game.bot_field.cells))
        self.assertEqual(0, len(game.player_field._ships))
        self.assertEqual(0, len(game.bot_field._ships))

        game.start()

        self.assertEqual(20, len(game.player_field.cells))
        self.assertEqual(20, len(game.bot_field.cells))
        self.assertEqual(10, len(game.player_field._ships))
        self.assertEqual(10, len(game.bot_field._ships))

        game = Game(4, 4, 2, 2)
        game.start()

        self.assertEqual(4, len(game.player_field.cells))
        self.assertEqual(4, len(game.bot_field.cells))
        self.assertEqual(3, len(game.player_field._ships))
        self.assertEqual(3, len(game.bot_field._ships))

    def test_empty_game(self):
        game = Game(10, 10, 4, 1)
        self.assertTrue(game.is_player_win())
        self.assertTrue(game.player_field.is_empty())
        self.assertTrue(game.bot_field.is_empty())
        game.start()
        self.assertFalse(game.is_player_win())
        self.assertFalse(game.player_field.is_empty())
        self.assertFalse(game.bot_field.is_empty())

    def test_restart_game(self):
        game = Game(10, 10, 2, 2)
        game.start()
        game.shot((0, 0))
        prev_game = deepcopy(game)
        game.restart()
        self.assertNotEqual(game, prev_game)

    def test_shot_game(self):
        game = Game(10, 10, 4, 2)
        game.start()
        self.assertIsNotNone(game.shot((0, 0)))
        self.assertTrue(len(game.bot_field.shots) > 0)
        if not game.player_current:
            self.assertIsNotNone(game.shot())
            self.assertTrue(len(game.player_field.shots) > 0)

        game = Game(4, 4, 2, 2)
        game.bot_field.add_ship(Ship([Cell(0, 0), Cell(0, 1)]))
        self.assertTrue(game.player_current)
        self.assertIsNotNone(game.shot((0, 2)))
        self.assertFalse(game.player_current)

        self.assertIsNotNone(game.shot())
        self.assertIsNotNone(game.shot((0, 0)))
        self.assertTrue(game.player_current)

    def test_end_game(self):
        game = Game(4, 4, 1, 2)
        game.start()
        self.assertIsNone(game.is_player_win())
        cell = game.bot_field.cells[0]
        game.shot((cell.x, cell.y))
        self.assertTrue(game.is_player_win())

    def test_save_load_game(self):
        game = Game(10, 10, 4, 2)
        game.start()
        game.save_game('test_save')
        save_game = Game.load_game('test_save')
        self.assertEqual(game, save_game)

    def test_load_bad(self):
        with self.assertRaises(FileNotFoundError):
            Game.load_game('BAD FILENAME')

    def test_undo(self):
        game = Game(10, 10, 1, 1)
        game.start()
        prev_game = deepcopy(game)

        game.shot((0, 0))
        self.assertTrue(len(game.bot_field.shots) > 0)
        self.assertTrue(len(prev_game.bot_field.shots) < 1)
        self.assertNotEqual(game, prev_game)
        game.undo()
        self.assertEqual(game, prev_game)
        self.assertTrue(game.player_current)

        for i in range(10):
            game.shot((0, i))
            game.shot()
        game.undo()
        self.assertTrue(game.can_undo())
        game.undo()
        self.assertFalse(game.can_undo())

    def test_eq_operator(self):
        game1 = Game(4, 4, 1, 2)
        game2 = Game(4, 4, 1, 1)
        game3 = Game(4, 4, 1, 1)
        self.assertNotEqual(game1, game2)
        self.assertEqual(game2, game3)

        field1 = Field(10, 10, 3)
        field2 = Field(9, 10, 3)
        field3 = Field(10, 10, 3)
        field4 = Field(10, 10, 4)
        self.assertNotEqual(field1, field2)
        self.assertNotEqual(field3, field4)
        self.assertEqual(field1, field3)
        field1.shot(Cell(0, 0))
        self.assertNotEqual(field1, field3)

        self.assertNotEqual(Cell(1, 0), Cell(0, 1))
        self.assertEqual(Cell(2, 3), Cell(2, 3))

        self.assertNotEqual(Ship([Cell(0, 1)]), Ship([Cell(0, 1), Cell(0, 2)]))
        self.assertEqual(Ship([Cell(3, 2), Cell(4, 2)]),
                         Ship([Cell(4, 2), Cell(3, 2)]))


class BotAITest(unittest.TestCase):

    def test_bot_shot_level_1(self):
        field = Field(10, 20, 5)
        result_shot = BotAI.shot_level_1(field)
        self.assertIsNotNone(result_shot)
        self.assertTrue(len(field.shots) > 0)

        for _ in range(100):
            result_shot = BotAI.shot_level_1(field)
            self.assertIsNotNone(result_shot)
        self.assertTrue(len(field.shots) > 100)

        field = Field(4, 4, 2)
        for _ in range(15):
            result_shot = BotAI.shot_level_1(field)
            self.assertIsNotNone(result_shot)
        self.assertTrue(len(field.shots) > 14)

    def test_bot_shot_level_2(self):
        field = Field(10, 20, 5)
        result_shot = BotAI.shot_level_2(field)
        self.assertIsNotNone(result_shot)
        self.assertTrue(len(field.shots) > 0)

        for _ in range(100):
            result_shot = BotAI.shot_level_2(field)
            self.assertIsNotNone(result_shot)
        self.assertTrue((len(field.shots) > 100))

        field = Field(4, 4, 2)
        for _ in range(15):
            result_shot = BotAI.shot_level_2(field)
            self.assertIsNotNone(result_shot)
        self.assertTrue(len(field.shots) > 14)

        BotAI._recommendation_level_2(0, 0, field)
        ans = [(1, 0), (0, 1), (3, 0), (0, 3)]
        for i in range(len(ans)):
            self.assertTrue(ans[i] in BotAI._recommend)


if __name__ == '__main__':
    unittest.main()
