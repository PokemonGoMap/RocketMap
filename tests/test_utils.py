import unittest
import os
from pogom import utils


class Args:
    locale = 'en'
    root_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    data_dir = 'static/dist/data'
    locales_dir = 'static/dist/locales'


class UtilsTest(unittest.TestCase):

    args = Args()

    def test_get_pokemon_name(self):
        self.assertEqual("Bulbasaur", utils.get_pokemon_name(self.args, 1))
        self.assertEqual("Dragonite", utils.get_pokemon_name(self.args, 149))

        # Unknown ID raises KeyError
        self.assertRaises(KeyError, utils.get_pokemon_name, self.args, 12367)
