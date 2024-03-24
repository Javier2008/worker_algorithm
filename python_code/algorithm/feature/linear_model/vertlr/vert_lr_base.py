#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021 Tianmian Tech. All Rights Reserved.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Copyright 2019 The FATE Authors. All Rights Reserved.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from google.protobuf import json_format

from algorithm.feature.linear_model.linear_model_base import BaseLinearModel
from algorithm.feature.linear_model.vertlr.param import VertLogisticParam
from algorithm.protobuf.generated import lr_model_meta_pb2, lr_model_param_pb2
from algorithm.secureprotol import PaillierEncrypt
from algorithm.transfer_variable.transfer_class.hetero_lr_transfer_variable import HeteroLRTransferVariable
from algorithm.util import consts
from algorithm.util.fate_operator import vec_dot
from common.common.log import getLogger

LOGGER = getLogger()


class VertLRBaseModel(BaseLinearModel):
    def __init__(self):
        super().__init__()
        self.model_name = 'VertLogisticRegression'
        self.model_param_name = 'VertLogisticRegressionParam'
        self.model_meta_name = 'VertLogisticRegressionMeta'
        self.mode = consts.HETERO
        self.aggregator = None
        self.cipher = None
        self.batch_generator = None
        self.gradient_loss_operator = None
        self.converge_procedure = None
        self.iter_transfer = None
        self.model_param = VertLogisticParam()
        self.is_serving_model = True

        self.in_one_vs_rest = False
        
    def _init_model(self, params):
        super()._init_model(params)
        self.encrypted_mode_calculator_param = params.encrypted_mode_calculator_param
        self.cipher_operator = PaillierEncrypt()
        self.transfer_variable = HeteroLRTransferVariable()
        self.cipher.register_paillier_keygen(self.transfer_variable)
        self.converge_procedure.register_convergence(self.transfer_variable)
        self.iter_transfer.register_iter_transfer(self.transfer_variable)
        self.batch_generator.register_batch_generator(self.transfer_variable)
        self.gradient_loss_operator.register_gradient_procedure(self.transfer_variable)

        # if params.optimizer == 'sqn':
        #     gradient_loss_operator = sqn_factory(self.role, params.sqn_param)
        #     gradient_loss_operator.register_gradient_computer(self.gradient_loss_operator)
        #     gradient_loss_operator.register_transfer_variable(self.transfer_variable)
        #     self.gradient_loss_operator = gradient_loss_operator
        #     LOGGER.debug("In _init_model, optimizer: {}, gradient_loss_operator: {}".format(
        #         params.optimizer, self.gradient_loss_operator
        #     ))

    def update_local_model(self, fore_gradient, data_inst, coef, **training_info):
        """
        update local model that transforms features of raw input

        This 'update_local_model' function serves as a handler on updating local model that transforms features of raw
        input into more representative features. We typically adopt neural networks as the local model, which is
        typically updated/trained based on stochastic gradient descent algorithm. For concrete implementation, please
        refer to 'vert_dnn_logistic_regression' folder.

        For this particular class (i.e., 'BaseLogisticRegression') that serves as a base class for neural-networks-based
        vert-logistic-regression model, the 'update_local_model' function will do nothing. In other words, no updating
        performed on the local model since there is no one.

        Parameters:
        ___________
        :param fore_gradient: a table holding fore gradient
        :param data_inst: a table holding instances of raw input of promoter side
        :param coef: coefficients of logistic regression model
        :param training_info: a dictionary holding training information
        """
        pass

    def transform(self, data_inst):
        """
        transform features of instances held by 'data_inst' table into more representative features

        This 'transform' function serves as a handler on transforming/extracting features from raw input 'data_inst' of
        promoter. It returns a table that holds instances with transformed features. In theory, we can use any model to
        transform features. Particularly, we would adopt neural network models such as auto-encoder or CNN to perform
        the feature transformation task. For concrete implementation, please refer to 'vert_dnn_logistic_regression'
        folder.

        For this particular class (i.e., 'BaseLogisticRegression') that serves as a base class for neural-networks-based
        vert-logistic-regression model, the 'transform' function will do nothing but return whatever that has been
        passed to it. In other words, no feature transformation performed on the raw input of promoter.

        Parameters:
        ___________
        :param data_inst: a table holding instances of raw input of promoter side
        :return: a table holding instances with transformed features
        """
        return data_inst

    def _get_meta(self):
        meta_protobuf_obj = lr_model_meta_pb2.LRModelMeta(penalty=self.model_param.penalty,
                                                          tol=self.model_param.tol,
                                                          alpha=self.alpha,
                                                          optimizer=self.model_param.optimizer,
                                                          batch_size=self.batch_size,
                                                          learning_rate=self.model_param.learning_rate,
                                                          max_iter=self.max_iter,
                                                          early_stop=self.model_param.early_stop,
                                                          fit_intercept=self.fit_intercept,
                                                          need_one_vs_rest=self.need_one_vs_rest)
        return meta_protobuf_obj
    
    def compute_wx(self, data_instances, coef_, intercept_=0):
        return data_instances.mapValues(lambda v: vec_dot(v.features, coef_) + intercept_)
    
    def _get_param(self):
        header = self.header
        LOGGER.debug("In get_param, header: {}".format(header))
        if header is None:
            param_protobuf_obj = lr_model_param_pb2.LRModelParam()
            return param_protobuf_obj
        if self.need_one_vs_rest:
            # one_vs_rest_class = list(map(str, self.one_vs_rest_obj.classes))
            one_vs_rest_result = self.one_vs_rest_obj.save(lr_model_param_pb2.SingleModel)
            single_result = {'header': header, 'need_one_vs_rest': True}
        else:
            one_vs_rest_result = None
            single_result = self.get_single_model_param()
            single_result['need_one_vs_rest'] = False
        single_result['one_vs_rest_result'] = one_vs_rest_result
        LOGGER.debug("in _get_param, single_result: {}".format(single_result))

        param_protobuf_obj = lr_model_param_pb2.LRModelParam(**single_result)
        json_result = json_format.MessageToJson(param_protobuf_obj)
        LOGGER.debug("json_result: {}".format(json_result))
        return param_protobuf_obj
    
    def get_single_model_param(self):
        weight_dict = {}
        LOGGER.debug("in get_single_model_param, model_weights: {}, coef: {}, header: {}".format(
            self.model_weights.unboxed, self.model_weights.coef_, self.header
        ))
        for idx, header_name in enumerate(self.header):
            coef_i = self.model_weights.coef_[idx]
            weight_dict[header_name] = coef_i

        result = {'iters': self.n_iter_,
                  'loss_history': self.loss_history,
                  'is_converged': self.is_converged,
                  'weight': weight_dict,
                  'intercept': self.model_weights.intercept_,
                  'header': self.header
                  }
        return result