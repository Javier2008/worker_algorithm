#
#  Created by yuyunfu
#   2022/9/21 
#

from algorithm.param.base_param import BaseParam

class FillNaParam(BaseParam):
    def __init__(self, default_value=0, default_fill_method=None, col_fill_method=None,
                 missing_impute=None, need_run=True):
        self.default_value = default_value
        self.default_fill_method = default_fill_method
        self.col_fill_method = col_fill_method
        self.missing_impute = missing_impute
        self.need_run = need_run

    def check(self):

        descr = "feature imputation param's "

        self.check_boolean(self.need_run, descr + "need_run")

        if self.default_fill_method is not None:
            self.fill_method = self.check_and_change_lower(self.default_fill_method,
                                                                   ['min', 'max', 'mean', 'designated'],
                                                                   f"{descr}fill_method ")
        if self.col_fill_method:
            for k, v in self.col_fill_method.items():
                if not isinstance(k, str):
                    raise Exception(f"{descr}col_fill_method should contain col name str")
                v = self.check_and_change_lower(v,
                                                ['min', 'max', 'mean', 'designated'],
                                                f"column method specified in {descr} col_missing_fill_method dict")
                self.col_fill_method[k] = v
        if self.missing_impute:
            if not isinstance(self.missing_impute, list):
                raise ValueError(f"{descr}missing_impute must be None or list.")

        return True