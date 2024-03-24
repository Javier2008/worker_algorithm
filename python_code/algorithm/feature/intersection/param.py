import copy

from algorithm.param.base_param import deprecated_param, BaseParam
from algorithm.param.intersect_param import RAWParam, RSAParam, DEFAULT_RANDOM_BIT, DHParam, IntersectCache, \
    IntersectPreProcessParam
from algorithm.util import LOGGER
from algorithm.util import consts


class EncodeParam(BaseParam):
    """
    Define the hash method for raw intersect method

    Parameters
    ----------
    salt: str
        the src data string will be str = str + salt, default by empty string

    encode_method: {"none", "md5", "sha1", "sha224", "sha256", "sha384", "sha512", "sm3"}
        the hash method of src data string, support md5, sha1, sha224, sha256, sha384, sha512, sm3, default by None

    base64: bool
        if True, the result of hash will be changed to base64, default by False
    """

    def __init__(self, salt='', encode_method='none', base64=False):
        super().__init__()
        self.salt = salt
        self.encode_method = encode_method
        self.base64 = base64

    def check(self):
        if type(self.salt).__name__ != "str":
            raise ValueError(
                "encode param's salt {} not supported, should be str type".format(
                    self.salt))

        descr = "encode param's "

        self.encode_method = self.check_and_change_lower(self.encode_method,
                                                         ["none", consts.MD5, consts.SHA1, consts.SHA224,
                                                          consts.SHA256, consts.SHA384, consts.SHA512,
                                                          consts.SM3],
                                                         descr)

        if type(self.base64).__name__ != "bool":
            raise ValueError(
                "hash param's base64 {} not supported, should be bool type".format(self.base64))

        LOGGER.debug("Finish EncodeParam check!")
        LOGGER.warning(f"'EncodeParam' will be replaced by 'RAWParam' in future release."
                       f"Please do not rely on current param naming in application.")
        return True


@deprecated_param("random_bit", "join_role", "with_encode", "encode_params", "intersect_cache_param",
                  "repeated_id_process", "repeated_id_owner", "allow_info_share", "info_owner", "with_sample_id")
class IntersectParam(BaseParam):
    """
    Define the intersect method

    Parameters
    ----------
    intersect_method: str
        it supports 'rsa', 'raw', and 'dh', default by 'rsa'

    random_bit: positive int
        it will define the size of blinding factor in rsa algorithm, default 128
        note that this param will be deprecated in future, please use random_bit in RSAParam instead

    sync_intersect_ids: bool
        In rsa, 'sync_intersect_ids' is True means guest or host will send intersect results to the others, and False will not.
        while in raw, 'sync_intersect_ids' is True means the role of "join_role" will send intersect results and the others will get them.
        Default by True.

    join_role: str
        role who joins ids, supports "guest" and "host" only and effective only for raw.
        If it is "guest", the host will send its ids to guest and find the intersection of
        ids in guest; if it is "host", the guest will send its ids to host. Default by "guest";
        note this param will be deprecated in future version, please use 'join_role' in raw_params instead

    only_output_key: bool
        if false, the results of intersection will include key and value which from input data; if true, it will just include key from input
        data and the value will be empty or filled by uniform string like "intersect_id"

    with_encode: bool
        if True, it will use hash method for intersect ids, effective for raw method only;
        note that this param will be deprecated in future version, please use 'use_hash' in raw_params;
        currently if this param is set to True,
        specification by 'encode_params' will be taken instead of 'raw_params'.

    encode_params: EncodeParam
        effective only when with_encode is True;
        this param will be deprecated in future version, use 'raw_params' in future implementation

    raw_params: RAWParam
        effective for raw method only

    rsa_params: RSAParam
        effective for rsa method only

    dh_params: DHParam
        effective for dh method only

    join_method: {'inner_join', 'left_join'}
        if 'left_join', participants will all include sample_id_generator's (imputed) ids in output,
        default 'inner_join'

    new_sample_id: bool
        whether to generate new id for sample_id_generator's ids,
        only effective when join_method is 'left_join' or when input data are instance with match id,
        default False

    sample_id_generator: str
        role whose ids are to be kept,
        effective only when join_method is 'left_join' or when input data are instance with match id,
        default 'guest'

    intersect_cache_param: IntersectCacheParam
        specification for cache generation,
        with ver1.7 and above, this param is ignored.

    run_cache: bool
        whether to store Host's encrypted ids, only valid when intersect method is 'rsa' or 'dh', default False

    cardinality_only: bool
        whether to output estimated intersection count(cardinality);
        if sync_cardinality is True, then sync cardinality count with host(s)

    sync_cardinality: bool
        whether to sync cardinality with all participants, default False,
        only effective when cardinality_only set to True

    run_preprocess: bool
        whether to run preprocess process, default False

    intersect_preprocess_params: IntersectPreProcessParam
        used for preprocessing and cardinality_only mode

    repeated_id_process: bool
        if true, intersection will process the ids which can be repeatable;
        in ver 1.7 and above,repeated id process
        will be automatically applied to data with instance id, this param will be ignored

    repeated_id_owner: str
        which role has the repeated id; in ver 1.7 and above, this param is ignored

    allow_info_share: bool
        in ver 1.7 and above, this param is ignored

    info_owner: str
        in ver 1.7 and above, this param is ignored

    with_sample_id: bool
        data with sample id or not, default False; in ver 1.7 and above, this param is ignored
    """

    def __init__(self, intersect_method: str = consts.RSA, random_bit=DEFAULT_RANDOM_BIT, sync_intersect_ids=True,
                 join_role=consts.GUEST, only_output_key: bool = False,
                 with_encode=False, encode_params=EncodeParam(),
                 raw_params=RAWParam(), rsa_params=RSAParam(), dh_params=DHParam(),
                 join_method=consts.INNER_JOIN, new_sample_id: bool = False, sample_id_generator=consts.GUEST,
                 intersect_cache_param=IntersectCache(), run_cache: bool = False,
                 cardinality_only: bool = False, sync_cardinality: bool = False,
                 run_preprocess: bool = False,
                 intersect_preprocess_params=IntersectPreProcessParam(),
                 repeated_id_process=False, repeated_id_owner=consts.GUEST,
                 with_sample_id=False, allow_info_share: bool = False, info_owner=consts.GUEST):
        super().__init__()
        self.intersect_method = intersect_method
        self.random_bit = random_bit
        self.sync_intersect_ids = sync_intersect_ids
        self.join_role = join_role
        self.with_encode = with_encode
        self.encode_params = copy.deepcopy(encode_params)
        self.raw_params = copy.deepcopy(raw_params)
        self.rsa_params = copy.deepcopy(rsa_params)
        self.only_output_key = only_output_key
        self.sample_id_generator = sample_id_generator
        self.intersect_cache_param = copy.deepcopy(intersect_cache_param)
        self.run_cache = run_cache
        self.repeated_id_process = repeated_id_process
        self.repeated_id_owner = repeated_id_owner
        self.allow_info_share = allow_info_share
        self.info_owner = info_owner
        self.with_sample_id = with_sample_id
        self.join_method = join_method
        self.new_sample_id = new_sample_id
        self.dh_params = copy.deepcopy(dh_params)
        self.cardinality_only = cardinality_only
        self.sync_cardinality = sync_cardinality
        self.run_preprocess = run_preprocess
        self.intersect_preprocess_params = copy.deepcopy(intersect_preprocess_params)

    def check(self):
        descr = "intersect param's "

        self.intersect_method = self.check_and_change_lower(self.intersect_method,
                                                            [consts.RSA, consts.RAW, consts.DH],
                                                            f"{descr}intersect_method")

        if self._warn_to_deprecate_param("random_bit", descr, "rsa_params' 'random_bit'"):
            if "rsa_params.random_bit" in self.get_user_feeded():
                raise ValueError(f"random_bit and rsa_params.random_bit should not be set simultaneously")
            self.rsa_params.random_bit = self.random_bit

        self.check_boolean(self.sync_intersect_ids, f"{descr}intersect_ids")

        if self._warn_to_deprecate_param("encode_param", "", ""):
            if "raw_params" in self.get_user_feeded():
                raise ValueError(f"encode_param and raw_params should not be set simultaneously")
            else:
                self.callback_param.callbacks = ["PerformanceEvaluate"]

        if self._warn_to_deprecate_param("join_role", descr, "raw_params' 'join_role'"):
            if "raw_params.join_role" in self.get_user_feeded():
                raise ValueError(f"join_role and raw_params.join_role should not be set simultaneously")
            self.raw_params.join_role = self.join_role

        self.check_boolean(self.only_output_key, f"{descr}only_output_key")

        self.join_method = self.check_and_change_lower(self.join_method, [consts.INNER_JOIN, consts.LEFT_JOIN],
                                                       f"{descr}join_method")
        self.check_boolean(self.new_sample_id, f"{descr}new_sample_id")
        self.sample_id_generator = self.check_and_change_lower(self.sample_id_generator,
                                                               [consts.GUEST, consts.HOST],
                                                               f"{descr}sample_id_generator")

        if self.join_method == consts.LEFT_JOIN:
            if not self.sync_intersect_ids:
                raise ValueError(f"Cannot perform left join without sync intersect ids")

        self.check_boolean(self.run_cache, f"{descr} run_cache")

        if self._warn_to_deprecate_param("encode_params", descr, "raw_params") or \
                self._warn_to_deprecate_param("with_encode", descr, "raw_params' 'use_hash'"):
            # self.encode_params.check()
            if "with_encode" in self.get_user_feeded() and "raw_params.use_hash" in self.get_user_feeded():
                raise ValueError(f"'raw_params' and 'encode_params' should not be set simultaneously.")
            if "raw_params" in self.get_user_feeded() and "encode_params" in self.get_user_feeded():
                raise ValueError(f"'raw_params' and 'encode_params' should not be set simultaneously.")
            LOGGER.warning(f"Param values from 'encode_params' will override 'raw_params' settings.")
            self.raw_params.use_hash = self.with_encode
            self.raw_params.hash_method = self.encode_params.encode_method
            self.raw_params.salt = self.encode_params.salt
            self.raw_params.base64 = self.encode_params.base64

        self.raw_params.check()
        self.rsa_params.check()
        self.dh_params.check()
        # self.intersect_cache_param.check()
        self.check_boolean(self.cardinality_only, f"{descr}cardinality_only")
        self.check_boolean(self.sync_cardinality, f"{descr}sync_cardinality")
        self.check_boolean(self.run_preprocess, f"{descr}run_preprocess")
        self.intersect_preprocess_params.check()
        if self.cardinality_only:
            if self.intersect_method not in [consts.RSA]:
                raise ValueError(f"cardinality-only mode only support rsa.")
            if self.intersect_method == consts.RSA and self.rsa_params.split_calculation:
                raise ValueError(f"cardinality-only mode only supports unified calculation.")
        if self.run_preprocess:
            if self.intersect_preprocess_params.false_positive_rate < 0.01:
                raise ValueError(f"for preprocessing ids, false_positive_rate must be no less than 0.01")
            if self.cardinality_only:
                raise ValueError(f"cardinality_only mode cannot run preprocessing.")
        if self.run_cache:
            if self.intersect_method not in [consts.RSA, consts.DH]:
                raise ValueError(f"Only rsa or dh method supports cache.")
            if self.intersect_method == consts.RSA and self.rsa_params.split_calculation:
                raise ValueError(f"RSA split_calculation does not support cache.")
            if self.cardinality_only:
                raise ValueError(f"cache is not available for cardinality_only mode.")
            if self.run_preprocess:
                raise ValueError(f"Preprocessing does not support cache.")

        deprecated_param_list = ["repeated_id_process", "repeated_id_owner", "intersect_cache_param",
                                 "allow_info_share", "info_owner", "with_sample_id"]
        for param in deprecated_param_list:
            self._warn_deprecated_param(param, descr)

        LOGGER.debug("Finish intersect parameter check!")
        return True