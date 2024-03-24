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
import importlib
import inspect
import os
import sys

from peewee import CharField, IntegerField, BigIntegerField, TextField, CompositeKey, BooleanField, BigAutoField

from common.common import file_utils, log, EngineType, conf_utils
from common.common.conf_utils import decrypt_database_config
from common.federation import FederationEngine
from common.metastore.base_model import DateTimeField, LongTextField, SerializedType
from common.metastore.base_model import JSONField, SerializedField, BaseModel

LOGGER = log.getLogger()

DATABASE = decrypt_database_config()
is_standalone = conf_utils.get_base_config("default_engines", {}).get(EngineType.FEDERATION).upper() == \
                FederationEngine.STANDALONE


def singleton(cls, *args, **kw):
    instances = {}

    def _singleton():
        key = str(cls) + str(os.getpid())
        if key not in instances:
            instances[key] = cls(*args, **kw)
        return instances[key]

    return _singleton


@singleton
class BaseDataBase(object):
    def __init__(self):
        database_config = DATABASE.copy()
        db_name = database_config.pop("name")
        if is_standalone:
            from playhouse.apsw_ext import APSWDatabase
            self.database_connection = APSWDatabase(file_utils.get_project_base_directory("sqlite.db"))
        else:
            from playhouse.pool import PooledMySQLDatabase
            self.database_connection = PooledMySQLDatabase(db_name, **database_config)


DB = BaseDataBase().database_connection


def close_connection():
    try:
        if DB:
            DB.close()
    except Exception as e:
        LOGGER.exception(e)


class DataBaseModel(BaseModel):
    class Meta:
        database = DB


@DB.connection_context()
def init_database_tables():
    members = inspect.getmembers(sys.modules[__name__], inspect.isclass)
    table_objs = []
    create_failed_list = []
    for name, obj in members:
        if obj != DataBaseModel and issubclass(obj, DataBaseModel):
            table_objs.append(obj)
            LOGGER.info(f"start create table {obj.__name__}")
            try:
                obj.create_table()
                LOGGER.info(f"create table success: {obj.__name__}")
            except Exception as e:
                LOGGER.exception(e)
                create_failed_list.append(obj.__name__)
    if create_failed_list:
        LOGGER.info(f"create tables failed: {create_failed_list}")
        raise Exception(f"create tables failed: {create_failed_list}")


class StorageConnectorModel(DataBaseModel):
    f_name = CharField(max_length=100, primary_key=True)
    f_engine = CharField(max_length=100, index=True)  # 'MYSQL'
    f_connector_info = JSONField()

    class Meta:
        db_table = "t_storage_connector"


class StorageTableMetaModel(DataBaseModel):
    f_name = CharField(max_length=100, index=True)
    f_namespace = CharField(max_length=100, index=True)
    f_address = JSONField()
    f_engine = CharField(max_length=100)  # 'EGGROLL', 'MYSQL'
    f_store_type = CharField(max_length=50, null=True)  # store type
    f_options = JSONField()
    f_partitions = IntegerField(null=True)

    f_id_delimiter = CharField(null=True)
    f_in_serialized = BooleanField(default=True)
    f_have_head = BooleanField(default=True)
    f_extend_sid = BooleanField(default=False)
    f_auto_increasing_sid = BooleanField(default=False)

    f_schema = SerializedField()
    f_count = BigIntegerField(null=True)
    f_part_of_data = SerializedField()
    f_origin = CharField(max_length=50, default='')
    f_disable = BooleanField(default=False)
    f_description = TextField(default='')

    f_read_access_time = BigIntegerField(null=True)
    f_read_access_date = DateTimeField(null=True)
    f_write_access_time = BigIntegerField(null=True)
    f_write_access_date = DateTimeField(null=True)

    class Meta:
        db_table = "t_storage_table_meta"
        primary_key = CompositeKey('f_name', 'f_namespace')


class SessionRecord(DataBaseModel):
    f_engine_session_id = CharField(max_length=150, null=False)
    f_manager_session_id = CharField(max_length=150, null=False)
    f_engine_type = CharField(max_length=10, index=True)
    f_engine_name = CharField(max_length=50, index=True)
    f_engine_address = JSONField()

    class Meta:
        db_table = "t_session_record"
        primary_key = CompositeKey("f_engine_type", "f_engine_name", "f_engine_session_id")


class ResultInfoDTO(DataBaseModel):
    id = BigAutoField(primary_key=True)
    job_id = CharField(max_length=25, index=True)
    component_name = TextField()
    task_id = CharField(max_length=100, null=True, index=True)
    task_version = BigIntegerField(null=True)
    name = CharField(max_length=180)
    key = CharField(max_length=200)
    value = LongTextField()
    type = IntegerField()  # 0 is data, 1 is meta
    
    class Meta:
        db_table = "result_info"


def from_dict_hook(in_dict: dict):
    if "type" in in_dict and "data" in in_dict:
        if in_dict["module"] is None:
            return in_dict["data"]
        else:
            return getattr(importlib.import_module(in_dict["module"]), in_dict["type"])(**in_dict["data"])
    else:
        return in_dict
    
class JsonSerializedField(SerializedField):
    def __init__(self, object_hook=from_dict_hook, object_pairs_hook=None, **kwargs):
        super().__init__(serialized_type=SerializedType.JSON, object_hook=object_hook,
                                                  object_pairs_hook=object_pairs_hook, **kwargs)
        
class ResultCacheDTO(DataBaseModel):
    cache_key = CharField(max_length=500)
    cache = JsonSerializedField()
    job_id = CharField(max_length=25, index=True, null=True)
    role = CharField(max_length=50, index=True, null=True)
    party_id = CharField(max_length=10, index=True, null=True)
    component_name = TextField(null=True)
    task_id = CharField(max_length=100, null=True)
    task_version = BigIntegerField(null=True, index=True)
    cache_name = CharField(max_length=50, null=True)
    ttl = BigIntegerField(default=0)
    
    class Meta:
        db_table = "cache_record"


class ResultDataInfoDTO(DataBaseModel):
    # multi-party common configuration
    job_id = CharField(max_length=25, index=True)
    component_name = TextField()
    task_id = CharField(max_length=100, null=True, index=True)
    task_version = BigIntegerField(null=True)
    
    data_name = CharField(max_length=30)
    # this party configuration
    role = CharField(max_length=50, index=True)
    party_id = CharField(max_length=10, index=True)
    table_name = CharField(max_length=500, null=True)
    table_namespace = CharField(max_length=500, null=True)
    description = TextField(null=True, default='')
    
    class Meta:
        db_table = "result_data_info"


class ResultSummary(DataBaseModel):
    id = BigAutoField(primary_key=True)
    job_id = CharField(max_length=25, index=True)
    role = CharField(max_length=25, index=True)
    party_id = CharField(max_length=10, index=True)
    component_name = TextField()
    task_id = CharField(max_length=50, null=True, index=True)
    task_version = CharField(max_length=50, null=True)
    summary = LongTextField()
    
    class Meta:
        db_table = "result_summary"


@DB.connection_context()
def bulk_insert_into_db(model, data_source, logger):
    try:
        try:
            DB.create_tables([model])
        except Exception as e:
            logger.exception(e)
        batch_size = 1000
        for i in range(0, len(data_source), batch_size):
            with DB.atomic():
                model.insert_many(data_source[i:i + batch_size]).execute()
        return len(data_source)
    except Exception as e:
        logger.exception(e)
        return 0