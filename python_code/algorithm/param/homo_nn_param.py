#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
import copy
import json
import typing
from types import SimpleNamespace

from algorithm.param.base_param import BaseParam
from algorithm.param.callback_param import CallbackParam
from algorithm.param.cross_validation_param import CrossValidationParam
from algorithm.param.predict_param import PredictParam


class HomoNNParam(BaseParam):
    """
    Parameters used for Homo Neural Network.

    Parameters
    ----------
    secure_aggregate : bool
        enable secure aggregation or not, defaults to True.
    aggregate_every_n_epoch : int
        aggregate model every n epoch, defaults to 1.
    config_type : {"nn", "keras", "tf"}
        config type
    nn_define : dict
        a dict represents the structure of neural network.
    optimizer : str or dict
        optimizer method, accept following types:
        1. a string, one of "Adadelta", "Adagrad", "Adam", "Adamax", "Nadam", "RMSprop", "SGD"
        2. a dict, with a required key-value pair keyed by "optimizer",
            with optional key-value pairs such as learning rate.
        defaults to "SGD"
    loss : str
        loss
    metrics: str or list of str
        metrics
    max_iter: int
        the maximum iteration for aggregation in training.
    batch_size : int
        batch size when updating model.
        -1 means use all data in a batch. i.e. Not to use mini-batch strategy.
        defaults to -1.
    early_stop : {'diff', 'weight_diff', 'abs'}
        Method used to judge converge or not.
            a)	diff： Use difference of loss between two iterations to judge whether converge.
            b)  weight_diff: Use difference between weights of two consecutive iterations
            c)	abs: Use the absolute value of loss to judge whether converge. i.e. if loss < eps, it is converged.
    encode_label : bool
        encode label to one_hot.
    """

    def __init__(
        self,
        api_version: int = 0,
        secure_aggregate: bool = True,
        aggregate_every_n_epoch: int = 1,
        config_type: str = "nn",
        nn_define: dict = None,
        optimizer: typing.Union[str, dict, SimpleNamespace] = "SGD",
        loss: str = None,
        metrics: typing.Union[str, list] = None,
        max_iter: int = 100,
        batch_size: int = -1,
        early_stop: typing.Union[str, dict, SimpleNamespace] = "diff",
        encode_label: bool = False,
        predict_param=PredictParam(),
        cv_param=CrossValidationParam(),
        callback_param=CallbackParam(),
    ):
        super(HomoNNParam, self).__init__()

        self.api_version = api_version

        self.secure_aggregate = secure_aggregate
        self.aggregate_every_n_epoch = aggregate_every_n_epoch

        self.config_type = config_type
        self.nn_define = nn_define or []
        self.encode_label = encode_label

        self.batch_size = batch_size
        self.max_iter = max_iter
        self.early_stop = early_stop
        self.metrics = metrics
        self.optimizer = optimizer
        self.loss = loss

        self.predict_param = copy.deepcopy(predict_param)
        self.cv_param = copy.deepcopy(cv_param)
        self.callback_param = copy.deepcopy(callback_param)

    def check(self):
        supported_config_type = ["nn", "keras", "pytorch"]
        if self.config_type not in supported_config_type:
            raise ValueError(f"config_type should be one of {supported_config_type}")
        self.early_stop = _parse_early_stop(self.early_stop)
        self.metrics = _parse_metrics(self.metrics)
        self.optimizer = _parse_optimizer(self.optimizer)

    def generate_pb(self):
        from algorithm.protobuf.generated import nn_model_meta_pb2

        pb = nn_model_meta_pb2.HomoNNParam()
        pb.secure_aggregate = self.secure_aggregate
        pb.encode_label = self.encode_label
        pb.aggregate_every_n_epoch = self.aggregate_every_n_epoch
        pb.config_type = self.config_type

        if self.config_type == "nn":
            for layer in self.nn_define:
                pb.nn_define.append(json.dumps(layer))
        elif self.config_type == "keras":
            pb.nn_define.append(json.dumps(self.nn_define))
        elif self.config_type == "pytorch":
            for layer in self.nn_define:
                pb.nn_define.append(json.dumps(layer))

        pb.batch_size = self.batch_size
        pb.max_iter = self.max_iter

        pb.early_stop.early_stop = self.early_stop.converge_func
        pb.early_stop.eps = self.early_stop.eps

        for metric in self.metrics:
            pb.metrics.append(metric)

        pb.optimizer.optimizer = self.optimizer.optimizer
        pb.optimizer.args = json.dumps(self.optimizer.kwargs)
        pb.loss = self.loss
        return pb

    def restore_from_pb(self, pb, is_warm_start_mode: bool = False):
        self.secure_aggregate = pb.secure_aggregate
        self.encode_label = pb.encode_label
        self.aggregate_every_n_epoch = pb.aggregate_every_n_epoch
        self.config_type = pb.config_type

        if self.config_type == "nn":
            for layer in pb.nn_define:
                self.nn_define.append(json.loads(layer))
        elif self.config_type == "keras":
            self.nn_define = json.loads(pb.nn_define[0])
        elif self.config_type == "pytorch":
            for layer in pb.nn_define:
                self.nn_define.append(json.loads(layer))
        else:
            raise ValueError(f"{self.config_type} is not supported")

        self.batch_size = pb.batch_size
        if not is_warm_start_mode:
            self.max_iter = pb.max_iter
            self.optimizer = _parse_optimizer(
                dict(optimizer=pb.optimizer.optimizer, **json.loads(pb.optimizer.args))
            )
        self.early_stop = _parse_early_stop(
            dict(early_stop=pb.early_stop.early_stop, eps=pb.early_stop.eps)
        )
        self.metrics = list(pb.metrics)
        self.loss = pb.loss
        return pb


def _parse_metrics(param):
    """
    Examples:

        1. "metrics": "Accuracy"
        2. "metrics": ["Accuracy"]
    """
    if not param:
        return []
    elif isinstance(param, str):
        return [param]
    elif isinstance(param, list):
        return param
    else:
        raise ValueError(f"invalid metrics type: {type(param)}")


def _parse_optimizer(param):
    """
    Examples:

        1. "optimize": "SGD"
        2. "optimize": {
                "optimizer": "SGD",
                "learning_rate": 0.05
            }
    """
    kwargs = {}
    if isinstance(param, str):
        return SimpleNamespace(optimizer=param, kwargs=kwargs)
    elif isinstance(param, dict):
        optimizer = param.get("optimizer", kwargs)
        if not optimizer:
            raise ValueError(f"optimizer config: {param} invalid")
        kwargs = {k: v for k, v in param.items() if k != "optimizer"}
        return SimpleNamespace(optimizer=optimizer, kwargs=kwargs)
    else:
        raise ValueError(f"invalid type for optimize: {type(param)}")


def _parse_early_stop(param):
    """
    Examples:

        1. "early_stop": "diff"
        2. "early_stop": {
                "early_stop": "diff",
                "eps": 0.0001
            }
    """
    default_eps = 0.0001
    if isinstance(param, str):
        return SimpleNamespace(converge_func=param, eps=default_eps)
    elif isinstance(param, dict):
        early_stop = param.get("early_stop", param.get("converge_func"))
        eps = param.get("eps", default_eps)
        if not early_stop:
            raise ValueError(f"early_stop config: {param} invalid")
        return SimpleNamespace(converge_func=early_stop, eps=eps)
    else:
        raise ValueError(f"invalid type for early_stop: {type(param)}")