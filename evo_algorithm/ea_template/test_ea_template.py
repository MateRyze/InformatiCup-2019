import ea_template
import unittest


class TestEA(unittest.TestCase):

    def setUp(self):
        ea_template.population.clear()
        ea_template.api_calls = 0
        ea_template.stop = False

    def test_init_population(self):
        self.assertEqual(len(ea_template.population), 0)
        ea_template.initPopulation(ea_template.INITIAL_POPULATION)
        self.assertEqual(len(ea_template.population),
                         ea_template.INITIAL_POPULATION)

    def test_selection(self):
        ea_template.initPopulation(ea_template.INITIAL_POPULATION)
        self.assertEqual(len(ea_template.population),
                         ea_template.INITIAL_POPULATION)
        ea_template.selection(ea_template.SELECTED_COUNT)
        self.assertEqual(len(ea_template.population),
                         ea_template.SELECTED_COUNT)

    def test_crossover(self):
        ea_template.initPopulation(ea_template.INITIAL_POPULATION)
        self.assertEqual(len(ea_template.population),
                         ea_template.INITIAL_POPULATION)
        ea_template.crossover()
        self.assertEqual(len(ea_template.population),
                         ea_template.INITIAL_POPULATION*2 - 1)

    def test_mutate(self):
        ea_template.initPopulation(ea_template.INITIAL_POPULATION)
        self.assertEqual(len(ea_template.population),
                         ea_template.INITIAL_POPULATION)
        ea_template.mutate(ea_template.DESIRED_CONFIDENCE)
        self.assertEqual(len(ea_template.population),
                         ea_template.INITIAL_POPULATION)

    def test_run_ea(self):
        ea_template.runEvoAlgorithm()
        # check if confidence is at least 90 % for all images (specification)
        self.assertTrue(all(individual["confidence"] >= 0.9 for individual in ea_template.population),
                        "The confidence is not at least 90 percent for 5 images!")


if __name__ == '__main__':
    unittest.main()

