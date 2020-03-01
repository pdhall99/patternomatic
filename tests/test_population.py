""" Unit testing file for GE module """
import unittest
import spacy

from PatternOmatic.ge.stats import Stats
from PatternOmatic.nlp.engine import dynagg as dgg
from PatternOmatic.ge.population import Population
from PatternOmatic.ge.individual import Individual
from PatternOmatic.settings.config import Config
from PatternOmatic.settings.literals import *

config = Config()


class TestPopulation(unittest.TestCase):
    """ Unit Test class for GE Population object """
    nlp = spacy.load("en_core_web_sm")

    samples = [nlp(u'I am a raccoon!'),
               nlp(u'You are a cat!'),
               nlp(u'Is she a rabbit?'),
               nlp(u'This is a test')]

    grammar = dgg(samples)

    stats = Stats()

    def test_initialize(self):
        p = Population(self.samples, self.grammar, self.stats)
        super().assertIsInstance(p.generation[0], Individual)

    def test_best_challenge(self):
        config.max_generations = 3
        config.fitness_function_type = FITNESS_BASIC
        p = Population(self.samples, self.grammar, self.stats)
        config.mutation_probability = 0.0
        p.generation[0] = Individual(self.samples, self.grammar, self.stats, '00101001011010000011001111001110')
        config.mutation_probability = 0.5
        p.evolve()

        super().assertGreaterEqual(p.best_individual.fitness_value, 0.4)

    def test_binary_tournament(self):
        config.max_generations = 3
        config.fitness_function_type = FITNESS_FULLMATCH
        config.selection_type = BINARY_TOURNAMENT
        p = Population(self.samples, self.grammar, self.stats)
        mating_pool = p._selection()

        super().assertNotEqual(p.generation, mating_pool)

    def test_k_tournament(self):
        config.selection_type = K_TOURNAMENT
        p = Population(self.samples, self.grammar, self.stats)
        with super().assertRaises(NotImplementedError):
            _ = p._selection()
        config.selection_type = BINARY_TOURNAMENT

    def test_random_one_point_crossover(self):
        config.max_generations = 3
        config.fitness_function_type = FITNESS_BASIC
        config.selection_type = BINARY_TOURNAMENT
        config.recombination_type = RANDOM_ONE_POINT_CROSSOVER
        p = Population(self.samples, self.grammar, self.stats)
        mating_pool = p._selection()
        p.offspring = p._recombination(mating_pool)
        super().assertNotEqual(p.generation, p.offspring)

    def test_mu_plus_lambda(self):
        config.replacement_type = MU_PLUS_LAMBDA
        p = Population(self.samples, self.grammar, self.stats)
        mating_pool = p._selection()
        p.offspring = p._recombination(mating_pool)
        p._replacement()
        super().assertListEqual(p.offspring, [])

    def test_mu_lambda_elite(self):
        config.replacement_type = MU_LAMBDA_WITH_ELITISM
        p = Population(self.samples, self.grammar, self.stats)
        mating_pool = p._selection()
        p.offspring = p._recombination(mating_pool)
        p._replacement()
        super().assertListEqual(p.offspring, [])

    def test_mu_lambda_no_elite(self):
        config.replacement_type = MU_LAMBDA_WITHOUT_ELITISM
        p = Population(self.samples, self.grammar, self.stats)
        mating_pool = p._selection()
        p.offspring = p._recombination(mating_pool)
        p._replacement()
        super().assertListEqual(p.offspring, [])

    def test_evolve(self):
        config.max_generations = 3
        config.fitness_function_type = FITNESS_BASIC
        p = Population(self.samples, self.grammar, self.stats)
        config.mutation_probability = 0.0
        p.generation[0] = Individual(self.samples, self.grammar, self.stats, '00101001011010000011001111001110')
        config.mutation_probability = 0.5
        p.evolve()
        super().assertGreaterEqual(p.generation[0].fitness_value, 0.4)


if __name__ == "__main__":
    unittest.main()
