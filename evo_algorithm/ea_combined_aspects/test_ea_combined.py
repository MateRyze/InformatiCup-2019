import ea_combined
import unittest


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
        # best count (5)
        ea_combined.selection(ea_combined.SELECTED_COUNT, 1)
        self.assertEqual(len(ea_combined.population),
                         ea_combined.SELECTED_COUNT)

    def test_crossover(self):
        resultsPassed = 0
        crossoverCount = 0
        # loop for statistical results
        for i in range(10):
            ea_combined.initPopulation(50)
            ea_combined.evalFitness(ea_combined.population)
            ea_combined.selection(ea_combined.SELECTED_COUNT, 2)
            crossoverResults = ea_combined.crossover()
            self.assertGreater(
                len(crossoverResults["before"]),
                0,
                "Crossover not possible, no images with same classes exist!"
            )
            self.assertGreater(len(crossoverResults["after"]), 1,
                               "No crossover results created!")
            # crossover should improve confidence
            results = ea_combined.evalFitness(crossoverResults["after"])
            print("before: ", len(
                crossoverResults["before"]),  crossoverResults["before"])
            print("after: ", len(results), results)

            crossoverCount += len(crossoverResults["before"])
            # [1,2,3,4] -> [(1, 2), (3, 4)]
            results = zip(results[0::2], results[1::2])
            for index, children in enumerate(results):
                parents = crossoverResults["before"][index]
                if (
                    children[0]["confidence"] > parents[0]["confidence"] and
                    children[0]["confidence"] > parents[1]["confidence"] and
                    children[0]["class"] == parents[0]["class"] or
                    children[1]["confidence"] > parents[0]["confidence"] and
                    children[1]["confidence"] > parents[1]["confidence"] and
                    children[1]["class"] == parents[0]["class"]
                ):
                    resultsPassed += 1
        self.assertEqual(resultsPassed, crossoverCount, "Improvement: " +
                         str(resultsPassed/crossoverCount*100) + "%")

    def test_mutate(self):
        ea_combined.initPopulation(ea_combined.INITIAL_POPULATION)
        self.assertEqual(len(ea_combined.population),
                         ea_combined.INITIAL_POPULATION)
        ea_combined.mutate(ea_combined.DESIRED_CONFIDENCE)
        self.assertEqual(len(ea_combined.population),
                         ea_combined.INITIAL_POPULATION)

    def test_run_ea(self):
        apiCallsList = []
        for i in range(10):
            print(
                "_____testing API calls, iteration: " +
                str(i+1) +
                "/10 _____"
            )
            ea_combined.runEvoAlgorithm()
            # check if confidence is at least 90 % for all images
            self.assertTrue(
                all(
                    individual["confidence"] >= 0.9 
                    for individual in ea_combined.population
                ),
                "The confidence is not at least 90 percent!"
            )
            # check for different classes
            self.assertTrue(
                len(
                    set(
                        individual["class"] 
                        for individual in ea_combined.population
                    )
                ) == 5,
                "Generated images contain class duplicates!"
            )
            apiCallsList.append(ea_combined.api_calls)
            ea_combined.saveImages("test_run")
            ea_combined.api_calls = 0
        print(apiCallsList)
        print("average: " + str(sum(apiCallsList)/len(apiCallsList)))


if __name__ == '__main__':
    unittest.main()
