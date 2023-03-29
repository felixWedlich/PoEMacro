import configparser
import unittest

from src.heist import GemPricer


class GemPricerTest(unittest.TestCase):
    def test_something(self):
        config = configparser.ConfigParser()
        config.read(r"C:\Users\Felix\IdeaProjects\Macro\settings.cfg")
        g = GemPricer(config)
        g._get_gem_data()
        g.get_gem_price("Anomalous Rage Support")


if __name__ == '__main__':
    unittest.main()
