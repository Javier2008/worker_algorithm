import copy

from algorithm.param.base_param import BaseParam, deprecated_param
from algorithm.param.feature_selection_param import UniqueValueParam, IVPercentileSelectionParam, IVTopKParam, \
    IVValueSelectionParam, VarianceOfCoeSelectionParam, OutlierColsSelectionParam, ManuallyFilterParam, \
    PercentageValueParam, CommonFilterParam, IVFilterParam, CorrelationFilterParam
from algorithm.param.ftl_param import deprecated_param_list
from algorithm.util import consts


@deprecated_param(*deprecated_param_list)
class FeatureSelectionParam(BaseParam):
    """
    Define the feature selection parameters.

    Parameters
    ----------
    select_col_indexes: list or int, default: -1
        Specify which columns need to calculated. -1 represent for all columns.

    select_names : list of string, default: []
        Specify which columns need to calculated. Each element in the list represent for a column name in header.

    filter_methods: list of ["manually", "iv_filter", "statistic_filter", "psi_filter", “hetero_sbt_filter", "homo_sbt_filter", "hetero_fast_sbt_filter", "percentage_value", "vif_filter", "correlation_filter"], default: ["manually"]
        The following methods will be deprecated in future version:
        "unique_value", "iv_value_thres", "iv_percentile",
        "coefficient_of_variation_value_thres", "outlier_cols"

        Specify the filter methods used in feature selection. The orders of filter used is depended on this list.
        Please be notified that, if a percentile method is used after some certain filter method,
        the percentile represent for the ratio of rest features.

        e.g. If you have 10 features at the beginning. After first filter method, you have 8 rest. Then, you want
        top 80% highest iv feature. Here, we will choose floor(0.8 * 8) = 6 features instead of 8.

    unique_param: UniqueValueParam
        filter the columns if all values in this feature is the same

    iv_value_param: IVValueSelectionParam
        Use information value to filter columns. If this method is set, a float threshold need to be provided.
        Filter those columns whose iv is smaller than threshold. Will be deprecated in the future.

    iv_percentile_param: IVPercentileSelectionParam
        Use information value to filter columns. If this method is set, a float ratio threshold
        need to be provided. Pick floor(ratio * feature_num) features with higher iv. If multiple features around
        the threshold are same, all those columns will be keep. Will be deprecated in the future.

    variance_coe_param: VarianceOfCoeSelectionParam
        Use coefficient of variation to judge whether filtered or not.
        Will be deprecated in the future.

    outlier_param: OutlierColsSelectionParam
        Filter columns whose certain percentile value is larger than a threshold.
        Will be deprecated in the future.

    percentage_value_param: PercentageValueParam
        Filter the columns that have a value that exceeds a certain percentage.

    iv_param: IVFilterParam
        Setting how to filter base on iv. It support take high mode only. All of "threshold",
        "top_k" and "top_percentile" are accepted. Check more details in CommonFilterParam. To
        use this filter, hetero-feature-binning module has to be provided.

    statistic_param: CommonFilterParam
        Setting how to filter base on statistic values. All of "threshold",
        "top_k" and "top_percentile" are accepted. Check more details in CommonFilterParam.
        To use this filter, data_statistic module has to be provided.

    psi_param: CommonFilterParam
        Setting how to filter base on psi values. All of "threshold",
        "top_k" and "top_percentile" are accepted. Its take_high properties should be False
        to choose lower psi features. Check more details in CommonFilterParam.
        To use this filter, data_statistic module has to be provided.

    need_run: bool, default True
        Indicate if this module needed to be run

    """

    def __init__(self, select_col_indexes=-1, select_names=None, filter_methods=None,
                 unique_param=UniqueValueParam(),
                 iv_value_param=IVValueSelectionParam(),
                 iv_percentile_param=IVPercentileSelectionParam(),
                 iv_top_k_param=IVTopKParam(),
                 variance_coe_param=VarianceOfCoeSelectionParam(),
                 outlier_param=OutlierColsSelectionParam(),
                 manually_param=ManuallyFilterParam(),
                 percentage_value_param=PercentageValueParam(),
                 iv_param=IVFilterParam(),
                 statistic_param=CommonFilterParam(metrics=consts.MEAN),
                 psi_param=CommonFilterParam(metrics=consts.PSI,
                                             take_high=False),
                 vif_param=CommonFilterParam(metrics=consts.VIF,
                                             threshold=5.0,
                                             take_high=False),
                 sbt_param=CommonFilterParam(metrics=consts.FEATURE_IMPORTANCE),
                 correlation_param=CorrelationFilterParam(),
                 need_run=True
                 ):
        super(FeatureSelectionParam, self).__init__()
        self.correlation_param = correlation_param
        self.vif_param = vif_param
        self.select_col_indexes = select_col_indexes
        if select_names is None:
            self.select_names = []
        else:
            self.select_names = select_names
        if filter_methods is None:
            self.filter_methods = [consts.MANUALLY_FILTER]
        else:
            self.filter_methods = filter_methods

        # deprecate in the future
        self.unique_param = copy.deepcopy(unique_param)
        self.iv_value_param = copy.deepcopy(iv_value_param)
        self.iv_percentile_param = copy.deepcopy(iv_percentile_param)
        self.iv_top_k_param = copy.deepcopy(iv_top_k_param)
        self.variance_coe_param = copy.deepcopy(variance_coe_param)
        self.outlier_param = copy.deepcopy(outlier_param)
        self.percentage_value_param = copy.deepcopy(percentage_value_param)

        self.manually_param = copy.deepcopy(manually_param)
        self.iv_param = copy.deepcopy(iv_param)
        self.statistic_param = copy.deepcopy(statistic_param)
        self.psi_param = copy.deepcopy(psi_param)
        self.sbt_param = copy.deepcopy(sbt_param)
        self.need_run = need_run

    def check(self):
        descr = "hetero feature selection param's"

        self.check_defined_type(self.filter_methods, descr, ['list'])

        for idx, method in enumerate(self.filter_methods):
            method = method.lower()
            self.check_valid_value(method, descr, [consts.UNIQUE_VALUE, consts.IV_VALUE_THRES, consts.IV_PERCENTILE,
                                                   consts.COEFFICIENT_OF_VARIATION_VALUE_THRES, consts.OUTLIER_COLS,
                                                   consts.MANUALLY_FILTER, consts.PERCENTAGE_VALUE,
                                                   consts.IV_FILTER, consts.STATISTIC_FILTER, consts.IV_TOP_K,
                                                   consts.PSI_FILTER, consts.HETERO_SBT_FILTER,
                                                   consts.HOMO_SBT_FILTER, consts.HETERO_FAST_SBT_FILTER,
                                                   consts.VIF_FILTER, consts.CORRELATION_FILTER])

            self.filter_methods[idx] = method

        self.check_defined_type(self.select_col_indexes, descr, ['list', 'int'])

        self.unique_param.check()
        self.iv_value_param.check()
        self.iv_percentile_param.check()
        self.iv_top_k_param.check()
        self.variance_coe_param.check()
        self.outlier_param.check()
        self.manually_param.check()
        self.percentage_value_param.check()

        self.iv_param.check()
        for th in self.iv_param.take_high:
            if not th:
                raise ValueError("Iv filter should take higher iv features")
        for m in self.iv_param.metrics:
            if m != consts.IV:
                raise ValueError("For iv filter, metrics should be 'iv'")

        self.statistic_param.check()
        self.psi_param.check()
        for th in self.psi_param.take_high:
            if th:
                raise ValueError("PSI filter should take lower psi features")
        for m in self.psi_param.metrics:
            if m != consts.PSI:
                raise ValueError("For psi filter, metrics should be 'psi'")

        self.sbt_param.check()
        for th in self.sbt_param.take_high:
            if not th:
                raise ValueError("SBT filter should take higher feature_importance features")
        for m in self.sbt_param.metrics:
            if m != consts.FEATURE_IMPORTANCE:
                raise ValueError("For SBT filter, metrics should be 'feature_importance'")

        self.vif_param.check()
        for m in self.vif_param.metrics:
            if m != consts.VIF:
                raise ValueError("For VIF filter, metrics should be 'vif'")

        self.correlation_param.check()

        self._warn_to_deprecate_param("iv_value_param", descr, "iv_param")
        self._warn_to_deprecate_param("iv_percentile_param", descr, "iv_param")
        self._warn_to_deprecate_param("iv_top_k_param", descr, "iv_param")
        self._warn_to_deprecate_param("variance_coe_param", descr, "statistic_param")
        self._warn_to_deprecate_param("unique_param", descr, "statistic_param")
        self._warn_to_deprecate_param("outlier_param", descr, "statistic_param")
