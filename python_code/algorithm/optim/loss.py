#
#  Created by yuyunfu
#   2022/9/27 
#
import numpy as np

from algorithm.optim import activation


class SigmoidBinaryCrossEntropyLoss(object):
    @staticmethod
    def initialize(y):
        """
        The initialize value if using cross entropy,
            this function mainly uses in secureboost's tree value initialize

        Parameters
        ----------
        y : Table
            The input data's labels

        Returns
        -------
        y_initialize : Table, the value of the table is a 1D numpy ndarray,
            which filled with zeros

        """
        return y.mapValues(lambda x: np.zeros(1)), np.zeros(1)

    @staticmethod
    def predict(value):
        """
        Predict method for using sigmoid cross entropy
            Formula : probability = 1.0 / (1.0 + exp(-value))

        Parameters
        ----------
        value : float, The input value of sigmoid function

        Returns
        -------
        probability : float, the output of sigmoid function

        """

        return activation.sigmoid(value)

    @staticmethod
    def compute_loss(y, y_prob):
        """
        The cross-entropy loss class for binary classification
            Formula : -(sum(y * log(y_prob) + (1 - y) * log(1 - y_prob)) / N)

        Parameters
        ----------
        y : Table
            The input data's labels

        y_prob : Table
            The predict probability.

        Returns
        -------
        log_loss : float, the binary cross entropy loss

        """
        logloss = y.join(y_prob, lambda y, yp: (-np.nan_to_num(y * np.log(yp) + (1 - y) * np.log(1 - yp)), 1))
        logloss_sum, sample_num = logloss.reduce(lambda tuple1, tuple2: (tuple1[0] + tuple2[0], tuple1[1] + tuple2[1]))
        return logloss_sum / sample_num

    @staticmethod
    def compute_grad(y, y_pred):
        """
        Compute the grad of sigmoid cross entropy function
            Formula : gradient = y_pred - y

        Parameters
        ----------
        y : int, label

        y_pred : float, the predict probability.

        Returns
        -------
        gradient : float, the gradient of binary cross entropy loss

        """
        return y_pred - y

    @staticmethod
    def compute_hess(y, y_pred):
        """
        Compute the hessian(second order derivative of sigmoid cross entropy loss
            Formula : hessian = y_pred * (1 - y_pred)


        Parameters
        ----------
        y : int, just use for function interface alignment

        y_pred : float, the predict probability

        Returns
        -------
        hess : float, the hessian of binary cross entropy loss

        """
        return y_pred * (1 - y_pred)

