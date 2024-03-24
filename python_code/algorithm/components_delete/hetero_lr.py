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

from .components import ComponentMeta

hetero_lr_cpn_meta = ComponentMeta("HeteroLR")


@hetero_lr_cpn_meta.bind_param
def hetero_lr_param():
    from algorithm.param.logistic_regression_param import HeteroLogisticParam

    return HeteroLogisticParam


@hetero_lr_cpn_meta.bind_runner.on_guest
def hetero_lr_runner_guest():
    from algorithm.feature.linear_model.coordinated_linear_model.logistic_regression.hetero_logistic_regression.hetero_lr_guest import (
        HeteroLRGuest, )

    return HeteroLRGuest


@hetero_lr_cpn_meta.bind_runner.on_host
def hetero_lr_runner_host():
    from algorithm.feature.linear_model.coordinated_linear_model.logistic_regression.hetero_logistic_regression.hetero_lr_host import (
        HeteroLRHost, )

    return HeteroLRHost


@hetero_lr_cpn_meta.bind_runner.on_arbiter
def hetero_lr_runner_arbiter():
    from algorithm.feature.linear_model.coordinated_linear_model.logistic_regression.hetero_logistic_regression.hetero_lr_arbiter import (
        HeteroLRArbiter, )

    return HeteroLRArbiter
