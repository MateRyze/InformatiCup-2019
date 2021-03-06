from kollektiv5gui.generators.EAGenerator import EAGenerator
import unittest


class Test_EA(unittest.TestCase):

    def setUp(self):
        self.generator = EAGenerator(True)
        self.generator.population.clear()
        self.generator.api_calls = 0

    def test_init_population(self):
        self.assertEqual(len(self.generator.population), 0)
        self.generator.initPopulation(self.generator.initialPopulationSize)
        self.assertEqual(len(self.generator.population),
                         self.generator.initialPopulationSize)

    def test_selection(self):
        self.generator.initPopulation(self.generator.initialPopulationSize)
        self.assertEqual(len(self.generator.population),
                         self.generator.initialPopulationSize)
        self.generator.selection(self.generator.targetPopulationSize, 2)
        # population should have at least two individuals after selection
        self.assertGreater(len(self.generator.population), 1)

    @unittest.skip("use only for statistics")
    def test_crossover(self):
        resultsPassed = 0
        crossoverCount = 0
        # loop for statistical results
        for i in range(10):
            self.generator.initPopulation(50)
            self.generator.evalFitness()
            self.generator.selection(self.generator.targetPopulationSize, 2)
            crossoverResults = self.generator.crossover()
            self.assertGreater(
                len(crossoverResults["before"]),
                0,
                "Crossover not possible, no images with same classes exist!"
            )
            self.assertGreater(len(crossoverResults["after"]), 1,
                               "No crossover results created!")
            # crossover should improve confidence
            self.generator.population = crossoverResults["after"]
            self.generator.evalFitness()
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
        self.generator.initPopulation(self.generator.targetPopulationSize)
        self.assertEqual(len(self.generator.population),
                         self.generator.targetPopulationSize)
        self.generator.mutate(self.generator.targetConfidence)
        # should not change population size
        self.assertEqual(len(self.generator.population),
                         self.generator.targetPopulationSize)

    def test_run_ea_once(self):
        self.generator.onFinished = lambda: None
        while not self.generator.hasFinished():
            self.generator.step(True)
        self.generator.selection(5, 1)
        # check if confidence is at least 90 % for all images
        self.assertTrue(
            all(
                individual["confidence"] >= 0.9
                for individual in self.generator.population
            ),
            "The confidence is not at least 90 percent!"
        )
        # check for different five classes
        self.assertTrue(
            len(
                set(
                    individual["class"]
                    for individual in self.generator.population
                )
            ) == 5,
            "Generated images contain class duplicates!"
        )

    @unittest.skip("use only for statistics")
    def test_run_ea_multiple(self):
        apiCallsList = []
        for i in range(10):
            print(
                "_____testing API calls, iteration: " +
                str(i+1) +
                "/10 _____"
            )
            while not self.generator._is_stopped and not self.generator.hasFinished:
                self.generator.step()
            # check if confidence is at least 90 % for all images
            self.assertTrue(
                all(
                    individual["confidence"] >= 0.9
                    for individual in self.generator.population
                ),
                "The confidence is not at least 90 percent!"
            )
            # check for different classes
            self.assertTrue(
                len(
                    set(
                        individual["class"]
                        for individual in self.generator.population
                    )
                ) == 5,
                "Generated images contain class duplicates!"
            )
            apiCallsList.append(self.generator.api_calls)
            # self.generator.saveImages("test_run")
            self.generator.api_calls = 0
        print(apiCallsList)
        print("average: " + str(sum(apiCallsList)/len(apiCallsList)))


if __name__ == '__main__':
    unittest.main()
