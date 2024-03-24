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

feldman_verifiable_sum_cpn_meta = ComponentMeta("FeldmanVerifiableSum")


@feldman_verifiable_sum_cpn_meta.bind_param
def feldman_verifiable_sum_param():
    from algorithm.param.feldman_verifiable_sum_param import FeldmanVerifiableSumParam

    return FeldmanVerifiableSumParam


@feldman_verifiable_sum_cpn_meta.bind_runner.on_guest
def feldman_verifiable_sum_guest_runner():
    from algorithm.statistic.feldman_verifiable_sum.feldman_verifiable_sum_guest import (
        FeldmanVerifiableSumGuest,
    )

    return FeldmanVerifiableSumGuest


@feldman_verifiable_sum_cpn_meta.bind_runner.on_host
def feldman_verifiable_sum_host_runner():
    from algorithm.statistic.feldman_verifiable_sum.feldman_verifiable_sum_host import (
        FeldmanVerifiableSumHost,
    )

    return FeldmanVerifiableSumHost
