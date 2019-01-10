import ea_combined
import unittest

# TODO: add more test functions


class TestEA(unittest.TestCase):

    def setUp(self):
        ea_combined.population.clear()
        ea_combined.api_calls = 0
        ea_combined.stop = False

    def test_init_population(self):
        self.assertEqual(len(ea_combined.population), 0)
        ea_combined.initPopulation(ea_combined.INITIAL_POPULATION)
        self.assertEqual(len(ea_combined.population),
                         ea_combined.INITIAL_POPULATION)

    def test_selection(self):
        ea_combined.initPopulation(ea_combined.INITIAL_POPULATION)
        self.assertEqual(len(ea_combined.population),
                         ea_combined.INITIAL_POPULATION)
        ea_combined.selection(ea_combined.SELECTED_COUNT)
        self.assertEqual(len(ea_combined.population),
                         ea_combined.SELECTED_COUNT)

    def test_crossover(self):
        ea_combined.initPopulation(ea_combined.INITIAL_POPULATION)
        self.assertEqual(len(ea_combined.population),
                         ea_combined.INITIAL_POPULATION)
        ea_combined.crossover()
        self.assertEqual(len(ea_combined.population),
                         ea_combined.INITIAL_POPULATION*2 - 1)

    def test_mutate(self):
        ea_combined.initPopulation(ea_combined.INITIAL_POPULATION)
        self.assertEqual(len(ea_combined.population),
                         ea_combined.INITIAL_POPULATION)
        ea_combined.mutate(ea_combined.DESIRED_CONFIDENCE)
        self.assertEqual(len(ea_combined.population),
                         ea_combined.INITIAL_POPULATION)
    
    def test_run_ea(self):
        ea_combined.runEvoAlgorithm()
        # check if confidence is at least 90 % for all images (specification)
        self.assertTrue(all(individual["confidence"] >= 0.9 for individual in ea_combined.population), "The confidence is not at least 90 percent for 5 images!")
        # check for different classes
        self.assertTrue(len(set(individual["class"] for individual in ea_combined.population)) == 5, "Generated images contain class duplicates!")
        # check for api call limit (FAST SOLUTION -> quality aspect)
        self.assertGreater(61, ea_combined.api_calls, "To much API calls -> slow solution :(")

if __name__ == '__main__':
    unittest.main()

                """ # distribute the contrast between the colors
            while(contrast(colors[0], colors[1]) < CONTRAST_RANGE[0] or contrast(colors[0], colors[1]) > CONTRAST_RANGE[1]):
                    colors = (
                        random.randint(COLORS_RANGE[0][0], COLORS_RANGE[0][1]),
                        random.randint(COLORS_RANGE[1][0], COLORS_RANGE[1][1]),
                        random.randint(COLORS_RANGE[2][0], COLORS_RANGE[2][1])) """


