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

import copy

from algorithm.param.callback_param import CallbackParam
from algorithm.param.cross_validation_param import CrossValidationParam
from algorithm.param.encrypt_param import EncryptParam
from algorithm.param.encrypted_mode_calculation_param import EncryptedModeCalculatorParam
from algorithm.param.init_model_param import InitParam
from algorithm.param.logistic_regression_param import LogisticParam
from algorithm.param.predict_param import PredictParam
from algorithm.util import consts


class HeteroSSHELRParam(LogisticParam):
    """
    Parameters used for Hetero SSHE Logistic Regression

    Parameters
    ----------
    penalty : str, 'L1', 'L2' or None. default: 'L2'
        Penalty method used in LR. If it is not None, weights are required to be reconstruct every iter.

    tol : float, default: 1e-4
        The tolerance of convergence

    alpha : float, default: 1.0
        Regularization strength coefficient.

    optimizer : str, 'sgd', 'rmsprop', 'adam', 'nesterov_momentum_sgd', or 'adagrad', default: 'sgd'
        Optimizer

    batch_size : int, default: -1
        Batch size when updating model. -1 means use all data in a batch. i.e. Not to use mini-batch strategy.

    learning_rate : float, default: 0.01
        Learning rate

    max_iter : int, default: 100
        The maximum iteration for training.

    early_stop : str, 'diff', 'weight_diff' or 'abs', default: 'diff'
        Method used to judge converge or not.
            a)	diff： Use difference of loss between two iterations to judge whether converge.
            b)  weight_diff: Use difference between weights of two consecutive iterations
            c)	abs: Use the absolute value of loss to judge whether converge. i.e. if loss < eps, it is converged.

    decay: int or float, default: 1
        Decay rate for learning rate. learning rate will follow the following decay schedule.
        lr = lr0/(1+decay*t) if decay_sqrt is False. If decay_sqrt is True, lr = lr0 / sqrt(1+decay*t)
        where t is the iter number.

    decay_sqrt: Bool, default: True
        lr = lr0/(1+decay*t) if decay_sqrt is False, otherwise, lr = lr0 / sqrt(1+decay*t)

    encrypt_param: EncryptParam object, default: default EncryptParam object
        encrypt param

    predict_param: PredictParam object, default: default PredictParam object
        predict param

    cv_param: CrossValidationParam object, default: default CrossValidationParam object
        cv param

    multi_class: str, 'ovr', default: 'ovr'
        If it is a multi_class task, indicate what strategy to use. Currently, support 'ovr' short for one_vs_rest only.

    reveal_strategy: str, "respectively", "encrypted_reveal_in_host", default: "respectively"
        "respectively": Means guest and host can reveal their own part of weights only.
        "encrypted_reveal_in_host": Means host can be revealed his weights in encrypted mode, and guest can be revealed in normal mode.

    reveal_every_iter: bool, default: False
        Whether reconstruct model weights every iteration. If so, Regularization is available.
        The performance will be better as well since the algorithm process is simplified.

    """

    def __init__(self, penalty='L2',
                 tol=1e-4, alpha=1.0, optimizer='sgd',
                 batch_size=-1, learning_rate=0.01, init_param=InitParam(),
                 max_iter=100, early_stop='diff', encrypt_param=EncryptParam(),
                 predict_param=PredictParam(), cv_param=CrossValidationParam(),
                 decay=1, decay_sqrt=True,
                 multi_class='ovr', use_mix_rand=True,
                 reveal_strategy="respectively",
                 reveal_every_iter=False,
                 callback_param=CallbackParam(),
                 encrypted_mode_calculator_param=EncryptedModeCalculatorParam()
                 ):
        super(HeteroSSHELRParam, self).__init__(penalty=penalty, tol=tol, alpha=alpha, optimizer=optimizer,
                                                batch_size=batch_size,
                                                learning_rate=learning_rate,
                                                init_param=init_param, max_iter=max_iter, early_stop=early_stop,
                                                predict_param=predict_param, cv_param=cv_param,
                                                decay=decay,
                                                decay_sqrt=decay_sqrt, multi_class=multi_class,
                                                encrypt_param=encrypt_param, callback_param=callback_param)
        self.use_mix_rand = use_mix_rand
        self.reveal_strategy = reveal_strategy
        self.reveal_every_iter = reveal_every_iter
        self.encrypted_mode_calculator_param = copy.deepcopy(encrypted_mode_calculator_param)

    def check(self):
        descr = "logistic_param's"
        super(HeteroSSHELRParam, self).check()
        self.check_boolean(self.reveal_every_iter, descr)
        if self.penalty is None:
            pass
        elif type(self.penalty).__name__ != "str":
            raise ValueError(
                "logistic_param's penalty {} not supported, should be str type".format(self.penalty))
        else:
            self.penalty = self.penalty.upper()
            """
            if self.penalty not in [consts.L1_PENALTY, consts.L2_PENALTY, consts.NONE.upper()]:
                raise ValueError(
                    "logistic_param's penalty not supported, penalty should be 'L1', 'L2' or 'NONE'")
            """
            if not self.reveal_every_iter:
                if self.penalty not in [consts.L2_PENALTY, consts.NONE.upper()]:
                    raise ValueError(
                        f"penalty should be 'L2' or 'none', when reveal_every_iter is False"
                    )

        if type(self.optimizer).__name__ != "str":
            raise ValueError(
                "logistic_param's optimizer {} not supported, should be str type".format(self.optimizer))
        else:
            self.optimizer = self.optimizer.lower()
            if self.reveal_every_iter:
                if self.optimizer not in ['sgd', 'rmsprop', 'adam', 'adagrad', 'nesterov_momentum_sgd']:
                    raise ValueError(
                        "When reveal_every_iter is True, "
                        "sshe logistic_param's optimizer not supported, optimizer should be"
                        " 'sgd', 'rmsprop', 'adam', 'nesterov_momentum_sgd', or 'adagrad'")
            else:
                if self.optimizer not in ['sgd', 'nesterov_momentum_sgd']:
                    raise ValueError("When reveal_every_iter is False, "
                                     "sshe logistic_param's optimizer not supported, optimizer should be"
                                     " 'sgd', 'nesterov_momentum_sgd'")

        if self.encrypt_param.method not in [consts.PAILLIER, None]:
            raise ValueError(
                "logistic_param's encrypted method support 'Paillier' or None only")

        if self.callback_param.validation_freqs is not None:
            if self.reveal_every_iter is False:
                raise ValueError(f"When reveal_every_iter is False, validation every iter"
                                 f" is not supported.")

        self.reveal_strategy = self.check_and_change_lower(self.reveal_strategy,
                                                           ["respectively", "encrypted_reveal_in_host"],
                                                           f"{descr} reveal_strategy")

        if self.reveal_strategy == "encrypted_reveal_in_host" and self.reveal_every_iter:
            raise PermissionError("reveal strategy: encrypted_reveal_in_host mode is not allow to reveal every iter.")
        self.encrypted_mode_calculator_param.check()
        return True
