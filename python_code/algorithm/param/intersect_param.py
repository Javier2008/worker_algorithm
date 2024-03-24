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

from algorithm.param.base_param import BaseParam
from algorithm.util import consts, LOGGER

def deprecated_param(*names):
    def _decorator(cls: "BaseParam"):
        deprecated = cls._get_or_init_deprecated_params_set()
        for name in names:
            deprecated.add(name)
        return cls

    return _decorator

DEFAULT_RANDOM_BIT = 128




class RAWParam(BaseParam):
    """
    Specify parameters for raw intersect method

    Parameters
    ----------
    use_hash: bool
        whether to hash ids for raw intersect

    salt: str
        the src data string will be str = str + salt, default by empty string

    hash_method: str
        the hash method of src data string, support md5, sha1, sha224, sha256, sha384, sha512, sm3, default by None

    base64: bool
        if True, the result of hash will be changed to base64, default by False

    join_role: {"guest", "host"}
        role who joins ids, supports "guest" and "host" only and effective only for raw.
        If it is "guest", the host will send its ids to guest and find the intersection of
        ids in guest; if it is "host", the guest will send its ids to host. Default by "guest";
    """

    def __init__(self, use_hash=False, salt='', hash_method='none', base64=False, join_role=consts.GUEST):
        super().__init__()
        self.use_hash = use_hash
        self.salt = salt
        self.hash_method = hash_method
        self.base64 = base64
        self.join_role = join_role

    def check(self):
        descr = "raw param's "

        self.check_boolean(self.use_hash, f"{descr}use_hash")
        self.check_string(self.salt, f"{descr}salt")

        self.hash_method = self.check_and_change_lower(self.hash_method,
                                                       ["none", consts.MD5, consts.SHA1, consts.SHA224,
                                                        consts.SHA256, consts.SHA384, consts.SHA512,
                                                        consts.SM3],
                                                       f"{descr}hash_method")

        self.check_boolean(self.base64, f"{descr}base_64")
        self.join_role = self.check_and_change_lower(self.join_role, [consts.GUEST, consts.HOST], f"{descr}join_role")

        LOGGER.debug("Finish RAWParam check!")
        return True


class RSAParam(BaseParam):
    """
    Specify parameters for RSA intersect method

    Parameters
    ----------
    salt: str
        the src data string will be str = str + salt, default ''

    hash_method: str
        the hash method of src data string, support sha256, sha384, sha512, sm3, default sha256

    final_hash_method: str
        the hash method of result data string, support md5, sha1, sha224, sha256, sha384, sha512, sm3, default sha256

    split_calculation: bool
        if True, Host & Guest split operations for faster performance, recommended on large data set

    random_base_fraction: positive float
        if not None, generate (fraction * public key id count) of r for encryption and reuse generated r;
        note that value greater than 0.99 will be taken as 1, and value less than 0.01 will be rounded up to 0.01

    key_length: int
        value >= 1024, bit count of rsa key, default 1024

    random_bit: positive int
        it will define the size of blinding factor in rsa algorithm, default 128

    """

    def __init__(self, salt='', hash_method='sha256', final_hash_method='sha256',
                 split_calculation=False, random_base_fraction=None, key_length=consts.DEFAULT_KEY_LENGTH,
                 random_bit=DEFAULT_RANDOM_BIT):
        super().__init__()
        self.salt = salt
        self.hash_method = hash_method
        self.final_hash_method = final_hash_method
        self.split_calculation = split_calculation
        self.random_base_fraction = random_base_fraction
        self.key_length = key_length
        self.random_bit = random_bit

    def check(self):
        descr = "rsa param's "
        self.check_string(self.salt, f"{descr}salt")

        self.hash_method = self.check_and_change_lower(self.hash_method,
                                                       [consts.SHA256, consts.SHA384, consts.SHA512, consts.SM3],
                                                       f"{descr}hash_method")

        self.final_hash_method = self.check_and_change_lower(self.final_hash_method,
                                                             [consts.MD5, consts.SHA1, consts.SHA224,
                                                              consts.SHA256, consts.SHA384, consts.SHA512,
                                                              consts.SM3],
                                                             f"{descr}final_hash_method")

        self.check_boolean(self.split_calculation, f"{descr}split_calculation")

        if self.random_base_fraction:
            self.check_positive_number(self.random_base_fraction, descr)
            self.check_decimal_float(self.random_base_fraction, f"{descr}random_base_fraction")

        self.check_positive_integer(self.key_length, f"{descr}key_length")
        if self.key_length < 1024:
            raise ValueError(f"key length must be >= 1024")
        self.check_positive_integer(self.random_bit, f"{descr}random_bit")

        LOGGER.debug("Finish RSAParam parameter check!")
        return True


class DHParam(BaseParam):
    """
    Define the hash method for DH intersect method

    Parameters
    ----------
    salt: str
        the src data string will be str = str + salt, default ''

    hash_method: str
        the hash method of src data string, support none, md5, sha1, sha 224, sha256, sha384, sha512, sm3, default sha256

    key_length: int, value >= 1024
        the key length of the commutative cipher p, default 1024

    """

    def __init__(self, salt='', hash_method='sha256', key_length=consts.DEFAULT_KEY_LENGTH):
        super().__init__()
        self.salt = salt
        self.hash_method = hash_method
        self.key_length = key_length

    def check(self):
        descr = "dh param's "
        self.check_string(self.salt, f"{descr}salt")

        self.hash_method = self.check_and_change_lower(self.hash_method,
                                                       ["none", consts.MD5, consts.SHA1, consts.SHA224,
                                                        consts.SHA256, consts.SHA384, consts.SHA512,
                                                        consts.SM3],
                                                       f"{descr}hash_method")

        self.check_positive_integer(self.key_length, f"{descr}key_length")
        if self.key_length < 1024:
            raise ValueError(f"key length must be >= 1024")

        LOGGER.debug("Finish DHParam parameter check!")
        return True


class IntersectCache(BaseParam):
    def __init__(self, use_cache=False, id_type=consts.PHONE, encrypt_type=consts.SHA256):
        """

        Parameters
        ----------
        use_cache: bool
            whether to use cached ids; with ver1.7 and above, this param is ignored
        id_type
            with ver1.7 and above, this param is ignored
        encrypt_type
            with ver1.7 and above, this param is ignored
        """
        super().__init__()
        self.use_cache = use_cache
        self.id_type = id_type
        self.encrypt_type = encrypt_type

    def check(self):
        descr = "intersect_cache param's "
        # self.check_boolean(self.use_cache, f"{descr}use_cache")

        self.check_and_change_lower(self.id_type,
                                    [consts.PHONE, consts.IMEI],
                                    f"{descr}id_type")
        self.check_and_change_lower(self.encrypt_type,
                                    [consts.MD5, consts.SHA256],
                                    f"{descr}encrypt_type")


class IntersectPreProcessParam(BaseParam):
    """
    Specify parameters for pre-processing and cardinality-only mode

    Parameters
    ----------
    false_positive_rate: float
        initial target false positive rate when creating Bloom Filter,
        must be <= 0.5, default 1e-3

    encrypt_method: str
        encrypt method for encrypting id when performing cardinality_only task,
        supports rsa only, default rsa;
        specify rsa parameter setting with RSAParam

    hash_method: str
        the hash method for inserting ids, support md5, sha1, sha 224, sha256, sha384, sha512, sm3,
        default sha256

    preprocess_method: str
        the hash method for encoding ids before insertion into filter, default sha256,
        only effective for preprocessing

    preprocess_salt: str
        salt to be appended to hash result by preprocess_method before insertion into filter,
        default '', only effective for preprocessing

    random_state: int
        seed for random salt generator when constructing hash functions,
        salt is appended to hash result by hash_method when performing insertion, default None

    filter_owner: str
        role that constructs filter, either guest or host, default guest,
        only effective for preprocessing

    """

    def __init__(self, false_positive_rate=1e-3, encrypt_method=consts.RSA, hash_method='sha256',
                 preprocess_method='sha256', preprocess_salt='', random_state=None, filter_owner=consts.GUEST):
        super().__init__()
        self.false_positive_rate = false_positive_rate
        self.encrypt_method = encrypt_method
        self.hash_method = hash_method
        self.preprocess_method = preprocess_method
        self.preprocess_salt = preprocess_salt
        self.random_state = random_state
        self.filter_owner = filter_owner

    def check(self):
        descr = "intersect preprocess param's false_positive_rate "
        self.check_decimal_float(self.false_positive_rate, descr)
        self.check_positive_number(self.false_positive_rate, descr)
        if self.false_positive_rate > 0.5:
            raise ValueError(f"{descr} must be positive float no greater than 0.5")

        descr = "intersect preprocess param's encrypt_method "
        self.encrypt_method = self.check_and_change_lower(self.encrypt_method, [consts.RSA], descr)

        descr = "intersect preprocess param's random_state "
        if self.random_state:
            self.check_nonnegative_number(self.random_state, descr)

        descr = "intersect preprocess param's hash_method "
        self.hash_method = self.check_and_change_lower(self.hash_method,
                                                       [consts.MD5, consts.SHA1, consts.SHA224,
                                                        consts.SHA256, consts.SHA384, consts.SHA512,
                                                        consts.SM3],
                                                       descr)
        descr = "intersect preprocess param's preprocess_salt "
        self.check_string(self.preprocess_salt, descr)

        descr = "intersect preprocess param's preprocess_method "
        self.preprocess_method = self.check_and_change_lower(self.preprocess_method,
                                                             [consts.MD5, consts.SHA1, consts.SHA224,
                                                              consts.SHA256, consts.SHA384, consts.SHA512,
                                                              consts.SM3],
                                                             descr)

        descr = "intersect preprocess param's filter_owner "
        self.filter_owner = self.check_and_change_lower(self.filter_owner,
                                                        [consts.GUEST, consts.HOST],
                                                        descr)

        LOGGER.debug("Finish IntersectPreProcessParam parameter check!")
        return True


