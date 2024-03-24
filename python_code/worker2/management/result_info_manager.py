#
#  Created by yuyunfu
#   2022/9/9 
#
from common.common.base_utils import current_timestamp
from common.common.log import getLogger
from common.metastore.db_models import DB, ResultInfoDTO, bulk_insert_into_db

LOGGER = getLogger()

class ResultInfo:
    def __init__(self, key, value: float, timestamp: float = None):
        self.key = key
        self.value = value
        self.timestamp = timestamp

class ResultInfoMeta(object):
    def __init__(self, name: str, metric_type: str = 'loss', extra_metas: dict = None):
        self.name = name
        self.metric_type = metric_type
        self.metas = {}
        if extra_metas:
            self.metas.update(extra_metas)
        self.metas['name'] = name
        self.metas['metric_type'] = metric_type

    def update_metas(self, metas: dict):
        self.metas.update(metas)

    def to_dict(self):
        return self.metas

    @classmethod
    def from_dict(cls, d: dict):
        metas = d.get("metas", {})
        if d.get("extra_metas"):
            metas.update(d["extra_metas"])
        return ResultInfoMeta(d.get("name"), d.get("metric_type"), extra_metas=metas)


#对应 MetricManager
class ResultInfoManager:
    def __init__(self, job_id: str, role: str, party_id: int,
                 component_name: str,
                 task_id: str = None,
                 task_version: int = None):
        self.job_id = job_id
        self.role = role
        self.party_id = party_id
        self.component_name = component_name
        self.task_id = task_id
        self.task_version = task_version

    @DB.connection_context()
    def read_result_info(self,  metric_name: str):
        results = []
        for k, v in self.read_result_info_from_db(metric_name, 1):
            results.append(ResultInfo(key=k, value=v))
        return results

    @DB.connection_context()
    def insert_result_info_into_db(self,  name: str, data_type: int, kv):
        try:
            result_info = ResultInfoDTO()
            result_info.job_id = self.job_id
            result_info.component_name = self.component_name
            result_info.task_id = self.task_id
            result_info.task_version = self.task_version
            result_info.name = name
            result_info.type = data_type
            default_db_source = result_info.to_dict()
            tracking_metric_data_source = []
            for k, v in kv:
                db_source = default_db_source.copy()
                db_source['key'] = k
                db_source['value'] = v
                db_source['f_create_time'] = current_timestamp()
                tracking_metric_data_source.append(db_source)
            bulk_insert_into_db(ResultInfoDTO, tracking_metric_data_source, LOGGER)
        except Exception as e:
            LOGGER.exception(
                "An exception where inserted infor {} of information  to database:\n".format(
                    e
                ))

    @DB.connection_context()
    def read_result_info_from_db(self, name: str, data_type):
        try:
            info = ResultInfoDTO.select(ResultInfoDTO.key, ResultInfoDTO.value).where(
                ResultInfoDTO.job_id == self.job_id,
                ResultInfoDTO.component_name == self.component_name,
                ResultInfoDTO.name == name,
                ResultInfoDTO.type == data_type
            )
        except Exception as e:
            LOGGER.exception(e)
            raise e
        return info

    @DB.connection_context()
    def clean_result_info(self):
        operate = ResultInfoDTO.delete().where(
            ResultInfoDTO.task_id == self.task_id
        )
        return operate.execute() > 0

    @DB.connection_context()
    def get_result_infos(self, job_level: bool = False):
        result_infos = ResultInfoDTO.select(
            ResultInfoDTO.name
        ).where(
            ResultInfoDTO.job_id == self.job_id,
            ResultInfoDTO.component_name == (self.component_name if not job_level else 'dag'),
        ).distinct()

        return result_infos

    @DB.connection_context()
    def read_result_infos(self):
        try:
            result_infos = ResultInfoDTO.select().where(
                ResultInfoDTO.job_id == self.job_id,
                ResultInfoDTO.component_name == self.component_name,
            )
            return [result_info for result_info in result_infos]
        except Exception as e:
            LOGGER.exception(e)
            raise e

    @DB.connection_context()
    def reload_result_info(self, result_info_manager):
        infos = result_info_manager.read_result_infos()
        for info in infos:
            result_info = ResultInfoDTO()
            result_info.job_id = self.job_id
            result_info.component_name = self.component_name
            result_info.task_id = self.task_id
            result_info.task_version = self.task_version
            result_info.name = info._name
            result_info.type = info.type
            result_info.key = info.key
            result_info.value = info.value
            result_info.save()
