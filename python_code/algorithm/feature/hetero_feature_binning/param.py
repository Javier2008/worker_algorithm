import copy

from algorithm.param import FeatureBinningParam, EncryptParam
from algorithm.param.feature_binning_param import TransformParam, OptimalBinningParam
from algorithm.util import consts


class HeteroFeatureBinningParam(FeatureBinningParam):
    def __init__(self, method=consts.QUANTILE,
                 compress_thres=consts.DEFAULT_COMPRESS_THRESHOLD,
                 head_size=consts.DEFAULT_HEAD_SIZE,
                 error=consts.DEFAULT_RELATIVE_ERROR,
                 bin_num=consts.G_BIN_NUM, bin_indexes=-1, bin_names=None, adjustment_factor=0.5,
                 transform_param=TransformParam(), optimal_binning_param=OptimalBinningParam(),
                 local_only=False, category_indexes=None, category_names=None,
                 encrypt_param=EncryptParam(),
                 need_run=True, skip_static=False):
        super(HeteroFeatureBinningParam, self).__init__(method=method, compress_thres=compress_thres,
                                                        head_size=head_size, error=error,
                                                        bin_num=bin_num, bin_indexes=bin_indexes,
                                                        bin_names=bin_names, adjustment_factor=adjustment_factor,
                                                        transform_param=transform_param,
                                                        category_indexes=category_indexes,
                                                        category_names=category_names,
                                                        need_run=need_run, local_only=local_only,
                                                        skip_static=skip_static)
        self.optimal_binning_param = copy.deepcopy(optimal_binning_param)
        self.encrypt_param = encrypt_param

    def check(self):
        descr = "Hetero Binning param's"
        super(HeteroFeatureBinningParam, self).check()
        self.check_valid_value(self.method, descr, [consts.QUANTILE, consts.BUCKET, consts.OPTIMAL])
        self.optimal_binning_param.check()
        self.encrypt_param.check()
        if self.encrypt_param.method != consts.PAILLIER:
            raise ValueError("Feature Binning support Paillier encrypt method only.")
        if self.skip_static and self.method == consts.OPTIMAL:
            raise ValueError("When skip_static, optimal binning is not supported.")
        self.transform_param.check()
        if self.skip_static and self.transform_param.transform_type == 'woe':
            raise ValueError("To use woe transform, skip_static should set as False")
