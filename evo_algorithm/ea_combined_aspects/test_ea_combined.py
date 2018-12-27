import ea_combined
import unittest

# TODO: add more test functions


class Test_EA(unittest.TestCase):

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
        ea_combined.initPopulation(120)
        ea_combined.evalFitness(ea_combined.population)
        ea_combined.selection(ea_combined.SELECTED_COUNT)
        crossoverResults = ea_combined.crossover()
        # crossover should improve confidence
        results = ea_combined.evalFitness(crossoverResults["after"])
        print("before: ", crossoverResults["before"])
        print("after: ", results)
        resultsPassed = 0
        for index, entry in enumerate(results):
            confidence = entry["confidence"]
            if confidence > crossoverResults["before"][index][0]["confidence"] and confidence > crossoverResults["before"][index][1]["confidence"] and entry["class"] == crossoverResults["before"][index][0]["class"]:
                resultsPassed += 1
        self.assertEqual(resultsPassed, len(crossoverResults["before"]), "no improvement after crossover")


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
