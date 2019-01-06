import ea_aspect_colors
import unittest

# TODO: add more test functions


class TestEA(unittest.TestCase):

    def setUp(self):
        ea_aspect_colors.population.clear()
        ea_aspect_colors.api_calls = 0
        ea_aspect_colors.stop = False

    def test_init_population(self):
        self.assertEqual(len(ea_aspect_colors.population), 0)
        ea_aspect_colors.initPopulation(ea_aspect_colors.INITIAL_POPULATION)
        self.assertEqual(len(ea_aspect_colors.population),
                         ea_aspect_colors.INITIAL_POPULATION)

    def test_selection(self):
        ea_aspect_colors.initPopulation(ea_aspect_colors.INITIAL_POPULATION)
        self.assertEqual(len(ea_aspect_colors.population),
                         ea_aspect_colors.INITIAL_POPULATION)
        ea_aspect_colors.selection(ea_aspect_colors.SELECTED_COUNT)
        self.assertEqual(len(ea_aspect_colors.population),
                         ea_aspect_colors.SELECTED_COUNT)

    def test_crossover(self):
        ea_aspect_colors.initPopulation(ea_aspect_colors.INITIAL_POPULATION)
        self.assertEqual(len(ea_aspect_colors.population),
                         ea_aspect_colors.INITIAL_POPULATION)
        ea_aspect_colors.crossover()
        self.assertEqual(len(ea_aspect_colors.population),
                         ea_aspect_colors.INITIAL_POPULATION*2 - 1)

    def test_mutate(self):
        ea_aspect_colors.initPopulation(ea_aspect_colors.INITIAL_POPULATION)
        self.assertEqual(len(ea_aspect_colors.population),
                         ea_aspect_colors.INITIAL_POPULATION)
        ea_aspect_colors.mutate(ea_aspect_colors.DESIRED_CONFIDENCE)
        self.assertEqual(len(ea_aspect_colors.population),
                         ea_aspect_colors.INITIAL_POPULATION)
    
    def test_run_ea(self):
        ea_aspect_colors.runEvoAlgorithm()
        # check if confidence is at least 90 % for all images (specification)
        self.assertTrue(all(individual["confidence"] >= 0.9 for individual in ea_aspect_colors.population), "The confidence is not at least 90 percent for 5 images!")
        # check for api call limit (FAST SOLUTION -> quality aspect)
        self.assertGreater(61, ea_aspect_colors.api_calls, "To much API calls -> slow solution :(")

if __name__ == '__main__':
    unittest.main()
