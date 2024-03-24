#
#  Created by yuyunfu
#   2022/9/13 
#
import typing
import uuid

from common import storage, session
from common.abc import CTableABC
from common.common import DTable
from common.common.base_utils import current_timestamp
from common.metastore.db_models import ResultCacheDTO, DB
from common.session import get_session
from worker2.entity.cache_data import CacheData


class ResultCacheManager:
    
    @classmethod
    def persistent(cls, task_id, cache_name: str, cache_data: typing.Dict[str, CTableABC], cache_meta: dict, output_storage_engine: str, output_storage_address: dict,
                   token=None) -> CacheData:
        output_namespace = f"output_cache_{task_id}"
        output_name = uuid.uuid1().hex
        cache = CacheData(name=cache_name, meta=cache_meta)
        for name, table in cache_data.items():
            table_meta = get_session().persistent(computing_table=table,
                                                    namespace=output_namespace,
                                                    name=f"{output_name}_{name}",
                                                    schema=None,
                                                    engine=output_storage_engine,
                                                    engine_address=output_storage_address,
                                                    token=token)
            cache.data[name] = DTable(namespace=table_meta.namespace, name=table_meta.name,
                                      partitions=table_meta.partitions)
        return cache

    @classmethod
    def load(cls, cache: CacheData) -> typing.Tuple[typing.Dict[str, CTableABC], dict]:
        cache_data = {}
        for name, table in cache.data.items():
            storage_table_meta = storage.StorageTableMeta(name=table.name, namespace=table.namespace)
            computing_table = session.get_computing_session().load(
                storage_table_meta.get_address(),
                schema=storage_table_meta.get_schema(),
                partitions=table.partitions)
            cache_data[name] = computing_table
        return cache_data, cache.meta

    @classmethod
    @DB.connection_context()
    def save_data(cls, cache: CacheData, job_id: str = None, role: str = None, party_id: int = None, component_name: str = None, task_id: str = None, task_version: int = None,
               cache_name: str = None):
        for attr in {"job_id", "component_name", "task_id", "task_version"}:
            if getattr(cache, attr) is None and locals().get(attr) is not None:
                setattr(cache, attr, locals().get(attr))
        record = ResultCacheDTO()
        record.create_time = current_timestamp()
        record.cache_key = uuid.uuid1().hex
        cache.key = record.f_cache_key
        record.cache = cache
        record.job_id = job_id
        record.role = role
        record.party_id = party_id
        record.component_name = component_name
        record.task_id = task_id
        record.task_version = task_version
        record.cache_name = cache_name
        rows = record.save(force_insert=True)
        if rows != 1:
            raise Exception("save cache tracking failed")
        return record.f_cache_key

    @classmethod
    @DB.connection_context()
    def find_data(cls, cache_key: str = None, role: str = None, party_id: int = None, component_name: str = None, cache_name: str = None,
              **kwargs) -> typing.List[CacheData]:
        if cache_key is not None:
            records = ResultCacheDTO.query(cache_key=cache_key)
        else:
            records = ResultCacheDTO.query(role=role, party_id=party_id, component_name=component_name,
                                        cache_name=cache_name, **kwargs)
        return [record.f_cache for record in records]

    @classmethod
    @DB.connection_context()
    def read_data(cls, role: str = None, party_id: int = None, component_name: str = None, **kwargs) -> typing.List[ResultCacheDTO]:
        records = ResultCacheDTO.query(role=role, party_id=party_id, component_name=component_name, **kwargs)
        return [record for record in records]