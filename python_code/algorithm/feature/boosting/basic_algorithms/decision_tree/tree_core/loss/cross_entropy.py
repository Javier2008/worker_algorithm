#
#  Copyright 2019 The FATE Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import numpy as np

from algorithm.optim import activation


class SoftmaxCrossEntropyLoss(object):
    @staticmethod
    def initialize(y, dims=1):
        """
        The initialize value if using softmax cross entropy loss,
            this function mainly uses in secureboost's tree value initialize

        Parameters
        ----------
        y : Table
            The input data's labels

        dims: the nums of different category labels

        Returns
        -------
        y_initialize : table, the value of the table is a 1D numpy ndarray
            with shape equals to dims, which filled with zeros

        """
        return y.mapValues(lambda x: np.zeros(dims)), np.zeros(dims)

    @staticmethod
    def predict(values):
        """
        Predict method for using softmax cross entropy
            Formula : probability(category_i) =
                exp(value(category_i)) / sum(exp(value(category_i))

        Parameters
        ----------
        values : ndarray, The input value of softmax function

        Returns
        -------
        probability : ndarray, the output of softmax function,
            the array shape is the sample as input values

        """
        return activation.softmax(values)

    @staticmethod
    def compute_loss(y, y_prob):
        """
        The cross-entropy loss class for binary classification
            Formula : -sum(log(prob(category_i))) / N

        Parameters
        ----------
        y : Table
            The input data's labels

        y_prob : Table, value of Table is ndarray
            The predict probability of each category.

        Returns
        -------
        softmax_loss : float, the softmax cross entropy loss

        """
        # np.sum(np.nan_to_num(y_i * np.log(y_pred)), axis=1)
        loss = y.join(y_prob, lambda y, yp_array: (-np.nan_to_num(np.log(yp_array[y])), 1))
        loss_sum, sample_num = loss.reduce(lambda tuple1, tuple2: (tuple1[0] + tuple2[0], tuple1[1] + tuple2[1]))
        return loss_sum / sample_num

    @staticmethod
    def compute_grad(y, y_pred):
        """
        Compute the grad of softmax cross entropy function

        Parameters
        ----------
        y : int, label

        y_pred : ndarray, the predict probability of each category.

        Returns
        -------
        gradient : ndarray, the gradient of softmax cross entropy loss

        """
        grad = y_pred.copy()
        grad[y] -= 1
        return grad

    @staticmethod
    def compute_hess(y, y_pred):
        """
        Compute the hessian of softmax cross entropy function

        Parameters
        ----------
        y : int, label

        y_pred : ndarray, the predict probability of each category.

        Returns
        -------
        hessian : ndarray, the hessian of softmax cross entropy loss

        """
        return y_pred * (1 - y_pred)
