import ea_template
import unittest

#TODO: add more test functions
class TestEA(unittest.TestCase):

    def setUp(self):
        ea_template.population.clear()

    def test_init_population(self):
        self.assertEqual(len(ea_template.population), 0)
        ea_template.initPopulation(ea_template.INITIAL_POPULATION)
        self.assertEqual(len(ea_template.population), ea_template.INITIAL_POPULATION)

    def test_selection(self):
        ea_template.initPopulation(ea_template.INITIAL_POPULATION)
        self.assertEqual(len(ea_template.population), ea_template.INITIAL_POPULATION)
        ea_template.selection(ea_template.SELECTED_COUNT)
        self.assertEqual(len(ea_template.population), ea_template.SELECTED_COUNT)

    def test_crossover(self):
        ea_template.initPopulation(ea_template.INITIAL_POPULATION)
        self.assertEqual(len(ea_template.population), ea_template.INITIAL_POPULATION)
        ea_template.crossover()
        self.assertEqual(len(ea_template.population), ea_template.INITIAL_POPULATION*2 - 1)


if __name__ == '__main__':
    unittest.main()
