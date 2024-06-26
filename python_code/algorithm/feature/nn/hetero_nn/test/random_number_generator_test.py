import random
import unittest

import numpy as np

from algorithm.feature.nn.hetero_nn.util.random_number_generator import RandomNumberGenerator
from algorithm.secureprotol.paillier_tensor import PaillierTensor
from common.session import computing_session as session


class TestRandomNumberGenerator(unittest.TestCase):
    def setUp(self):
        session.init("test_random_number" + str(random.random()))
        self.rng_gen = RandomNumberGenerator()

    def test_generate_random_number(self):
        data = np.ones((1, 3))
        random_data = self.rng_gen.generate_random_number(data.shape)

        self.assertTrue(random_data.shape == data.shape)

    def test_fast_generate_random_number(self):
        data = np.ones((1000, 100))

        random_data = self.rng_gen.fast_generate_random_number(data.shape)
        self.assertTrue(isinstance(random_data, PaillierTensor))
        self.assertTrue(tuple(random_data.shape) == tuple(data.shape))

    def tearDown(self):
        session.stop()


if __name__ == '__main__':
    unittest.main()
