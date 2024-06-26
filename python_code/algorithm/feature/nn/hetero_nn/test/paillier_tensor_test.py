import random
import unittest

import numpy as np

from algorithm.secureprotol.paillier_tensor import PaillierTensor
from algorithm.util import consts
from common.session import computing_session as session


class TestPaillierTensor(unittest.TestCase):
    def setUp(self):
        session.init("test_paillier_tensor" + str(random.random()))
        self.data1 = np.ones((1000, 10))
        self.data2 = np.ones((1000, 10))
        self.paillier_tensor1 = PaillierTensor(self.data1, partitions=10)
        self.paillier_tensor2 = PaillierTensor(self.data2, partitions=10)

    def test_tensor_add(self):
        paillier_tensor = self.paillier_tensor1 + self.paillier_tensor2
        self.assertTrue(isinstance(paillier_tensor, PaillierTensor))
        self.assertTrue(paillier_tensor.shape == self.paillier_tensor1.shape)
        arr = paillier_tensor.numpy()
        self.assertTrue(abs(arr.sum() - 20000) < consts.FLOAT_ZERO)

    def test_ndarray_add(self):
        paillier_tensor = self.paillier_tensor1 + np.ones(10)
        self.assertTrue(isinstance(paillier_tensor, PaillierTensor))
        self.assertTrue(paillier_tensor.shape == self.paillier_tensor1.shape)
        arr = paillier_tensor.numpy()
        self.assertTrue(abs(arr.sum() - 20000) < consts.FLOAT_ZERO)

    def test_tensor_sub(self):
        paillier_tensor = self.paillier_tensor1 - self.paillier_tensor2
        self.assertTrue(isinstance(paillier_tensor, PaillierTensor))
        self.assertTrue(paillier_tensor.shape == self.paillier_tensor1.shape)

        arr = paillier_tensor.numpy()
        self.assertTrue(abs(arr.sum()) < consts.FLOAT_ZERO)

    def test_tensor_sub(self):
        paillier_tensor = self.paillier_tensor1 - np.ones(10)
        self.assertTrue(isinstance(paillier_tensor, PaillierTensor))
        self.assertTrue(paillier_tensor.shape == self.paillier_tensor1.shape)
        arr = paillier_tensor.numpy()
        self.assertTrue(abs(arr.sum()) < consts.FLOAT_ZERO)

    def test_constant_mul(self):
        paillier_tensor = self.paillier_tensor1 * 10
        self.assertTrue(isinstance(paillier_tensor, PaillierTensor))
        self.assertTrue(paillier_tensor.shape == self.paillier_tensor1.shape)
        arr = paillier_tensor.numpy()
        self.assertTrue(abs(arr.sum() - 100000) < consts.FLOAT_ZERO)

    def test_inverse(self):
        paillier_tensor = self.paillier_tensor2.T
        self.assertTrue(isinstance(paillier_tensor, PaillierTensor))
        self.assertTrue(paillier_tensor.shape == tuple([10, 1000]))

    def test_get_partition(self):
        self.assertTrue(self.paillier_tensor1.partitions == 10)

    def test_mean(self):
        self.assertTrue(abs(self.paillier_tensor1.mean() - 1.0) < consts.FLOAT_ZERO)

    def test_encrypt_and_decrypt(self):
        from algorithm.secureprotol import PaillierEncrypt
        from algorithm.secureprotol.encrypt_mode import EncryptModeCalculator
        encrypter = PaillierEncrypt()
        encrypter.generate_key(1024)

        encrypted_calculator = EncryptModeCalculator(encrypter,
                                                     "fast")

        encrypter_tensor = self.paillier_tensor1.encrypt(encrypted_calculator)
        decrypted_tensor = encrypter_tensor.decrypt(encrypter)

        self.assertTrue(isinstance(encrypter_tensor, PaillierTensor))
        self.assertTrue(isinstance(decrypted_tensor, PaillierTensor))

        arr = decrypted_tensor.numpy()
        self.assertTrue(abs(arr.sum() - 10000) < consts.FLOAT_ZERO)

    def tearDown(self):
        session.stop()


if __name__ == '__main__':
    unittest.main()
