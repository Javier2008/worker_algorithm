#
#  Created by yuyunfu
#   2022/9/9 
#
import base64
import copy
import operator
import typing
import uuid

from algorithm.model_base import Metric
from common.abc import CTableABC
from common.common import Party
from common.common.log import getLogger
from common.computing import ComputingEngine
from common.federation import FederationEngine
from common.metastore.db_models import DB, ResultDataInfoDTO
from worker2.entity.cache_data import CacheData
from worker2.entity.taskConfiguration import TaskConfiguration
from worker2.management.result_cache_manager import ResultCacheManager
from worker2.management.result_data_manager import ResultDataManager
from worker2.management.result_info_manager import ResultInfoManager, ResultInfoMeta
from worker2.management.result_model_manager import ResultModelManager
from worker2.management.result_summary_manager import ResultSummaryManager

LOGGER = getLogger()

def generate_session_id(task_id, task_version, role, party_id, suffix=None, random_end=False):
    items = [task_id, str(task_version), role, str(party_id)]
    if suffix:
        items.append(suffix)
    if random_end:
        items.append(uuid.uuid1().hex)
    return "_".join(items)


def gen_party_model_id(model_id, role, party_id):
    return '#'.join([role, str(party_id), model_id]) if model_id else None

def generate_task_version_id(task_id, task_version):
    return "{}_{}".format(task_id, task_version)

#对应tracker
class ResultManagement:
    def __init__(self, job_id: str, role: str, party_id: int,
                 model_id: str = None,
                 model_version: str = None,
                 component_name: str = None,
                 component_module_name: str = None,
                 task_id: str = None,
                 task_version: int = None,
                 task_configuration: TaskConfiguration = None
                 ):
        self.task_version = task_version
        self.job_id = job_id
        self.job_parameters = task_configuration
        self.role = role
        self.party_id = party_id
        self.component_name = component_name
        self.module_name = component_module_name
        self.task_id = task_id

        self.model_id = model_id
        self.party_model_id = gen_party_model_id(model_id=model_id, role=role, party_id=party_id)
        self.model_version = model_version
        self.pipelined_model = None
        if self.party_model_id and self.model_version:
            self.pipelined_model = ResultModelManager(model_id=self.party_model_id,
                                                                   model_version=self.model_version)
        self.metric_manager = ResultInfoManager(job_id=self.job_id, role=self.role, party_id=self.party_id,
                                                component_name=self.component_name,
                                                task_id=self.task_id, task_version= task_version)
        self.data_manager = ResultDataManager(task_id, job_id, component_name, task_version, party_id, role)
        self.summary_manager = ResultSummaryManager(job_id, component_name, role, party_id, task_id, task_version)
        
    def save_metric_data(self, metric_namespace: str, metric_name: str, metrics: typing.List[Metric], job_level=False):
        LOGGER.info(
            'save component {} on {} {} {} {} metric data'.format(self.component_name, self.role,
                                                                  self.party_id, metric_namespace, metric_name))
        kv = []
        for metric in metrics:
            kv.append((metric.key, metric.value))
        self.metric_manager.insert_result_info_into_db( metric_name, 1, kv)

    def get_job_metric_data(self, metric_namespace: str, metric_name: str):
        return self.read_metric_data(metric_namespace=metric_namespace, metric_name=metric_name, job_level=True)

    def get_metric_data(self, metric_namespace: str, metric_name: str):
        return self.read_metric_data(metric_namespace=metric_namespace, metric_name=metric_name, job_level=False)

    @DB.connection_context()
    def read_metric_data(self, metric_namespace: str, metric_name: str, job_level=False):
        metrics = []
        for k, v in self.metric_manager.read_result_info_from_db(metric_name, 1):
            metrics.append(Metric(key=k, value=v))
        return metrics

    def save_metric_meta(self, metric_namespace: str, metric_name: str, metric_meta,
                         job_level: bool = False):
        LOGGER.info(
            'save component {} on {} {} {} {} metric meta'.format(self.component_name, self.role,
                                                                  self.party_id, metric_namespace, metric_name))
        self.metric_manager.insert_result_info_into_db( metric_name, 0, metric_meta.items())

    @DB.connection_context()
    def get_metric_meta(self, metric_name: str, job_level: bool = False):
        kv = dict()
        for k, v in self.metric_manager.read_result_info_from_db(metric_name, 0):
            kv[k] = v
        return ResultInfoMeta(name=kv.get('name'), metric_type=kv.get('metric_type'), extra_metas=kv)

    def save_output_data(self, computing_table, output_storage_engine, output_storage_address=None,
                         output_table_namespace=None, output_table_name=None, schema=None, token=None, need_read=True):
        return self.data_manager.save_data(computing_table, output_storage_engine, output_storage_address, output_table_namespace,
                                           output_table_name, schema, token, need_read)
        
    def get_output_data_table(self, output_data_infos):
        
        return self.data_manager.read_data_table(output_data_infos)

    def init_pipeline_model(self):
        '''
        此函数应该在创建job的时候调用，一个job，一个模型只需要调用一次
        :return:
        '''
        self.pipelined_model.create_job_model()

    def save_output_model(self, model_buffers: dict, model_alias: str):
        if model_buffers:
            self.pipelined_model.save_component_model(component_name=self.component_name,
                                                      component_module_name=self.module_name,
                                                      model_alias=model_alias,
                                                      model_buffers=model_buffers)

    def get_output_model(self, model_alias, parse=True, output_json=False):
        return self.read_output_model(model_alias=model_alias,
                                      parse=parse,
                                      output_json=output_json)

    def write_output_model(self, component_model):
        self.pipelined_model.write_component_model(component_model)

    def read_output_model(self, model_alias, parse=True, output_json=False):
        res = self.pipelined_model.read_component_model(component_name=self.component_name,
                                                         model_alias=model_alias,
                                                         parse=parse,
                                                         output_json=output_json)

        model_buffers = {}
        for model_name, v in res.items():
            model_buffers[model_name] = (v[0], base64.b64decode(v[1].encode()))
        return model_buffers

    def collect_model(self):
        model_buffers = self.pipelined_model.collect_models()
        return model_buffers

    def save_pipeline_model(self, pipeline_buffer_object):
        self.pipelined_model.save_job_model(pipeline_buffer_object)

    def get_pipeline_model(self):
        return self.pipelined_model.read_job_model()

    def get_component_define(self):
        return self.pipelined_model.get_component_define(component_name=self.component_name)

    def save_output_cache(self, cache_data: typing.Dict[str, CTableABC], cache_meta: dict, cache_name,
                          output_storage_engine, output_storage_address: dict, token=None):
        
        cache = ResultCacheManager.persistent(self.task_id, cache_name, cache_data, cache_meta,
                                        output_storage_engine, output_storage_address, token=token)
        cache_key = self.tracking_output_cache(cache=cache, cache_name=cache_name)
        return cache_key

    def tracking_output_cache(self, cache: CacheData, cache_name: str) -> str:
        cache_key = ResultCacheManager.save_data(cache=cache,
                                        job_id=self.job_id,
                                        role=self.role,
                                        party_id=self.party_id,
                                        component_name=self.component_name,
                                        task_id=self.task_id,
                        
                                        cache_name=cache_name)
        LOGGER.info(
            f"tracking {self.task_id}  output cache, cache key is {cache_key}")
        return cache_key

    def get_output_cache(self, cache_key=None, cache_name=None):
        caches = self.query_output_cache(cache_key=cache_key, cache_name=cache_name)
        if caches:
            return ResultCacheManager.load(cache=caches[0])
        else:
            return None, None

    def query_output_cache(self, cache_key=None, cache_name=None) -> typing.List[CacheData]:
        caches = ResultCacheManager.find_data(job_id=self.job_id, role=self.role, party_id=self.party_id,
                                    component_name=self.component_name, cache_name=cache_name, cache_key=cache_key)
        group = {}
        # only the latest version of the task output is retrieved
        for cache in caches:
            group_key = f"{cache.task_id}-{cache.name}"
            if group_key not in group:
                group[group_key] = cache
            elif cache.task_version > group[group_key].task_version:
                group[group_key] = cache
        return list(group.values())

    def query_output_cache_record(self):
        return ResultCacheManager.find_data(job_id=self.job_id, role=self.role, party_id=self.party_id,
                                         component_name=self.component_name)

    def insert_summary_into_db(self, summary_data: dict):
        self.summary_manager.save_data(summary_data)

    def read_summary_from_db(self):
        return self.summary_manager.read_data()


    def log_output_data_info(self, data_name: str, table_namespace: str, table_name: str):
        self.data_manager.save_data_info(data_name=data_name, table_namespace=table_namespace,
                                             table_name=table_name)


    # def save_as_table(self, computing_table, name, namespace):
    #     if self.job_parameters.storage_engine == StorageEngine.LINKIS_HIVE:
    #         return
    #     self.save_output_data(computing_table=computing_table,
    #                           output_storage_engine=self.job_parameters.storage_engine,
    #                           output_storage_address=self.job_parameters.engines_address.get(EngineType.STORAGE, {}),
    #                           output_table_namespace=namespace, output_table_name=name)

    @DB.connection_context()
    def clean_metrics(self):
        return self.metric_manager.clean_result_info()

    @DB.connection_context()
    def get_metric_list(self, job_level: bool = False):
        return self.metric_manager.get_result_infos(job_level=job_level)

    @DB.connection_context()
    def reload_metric(self, source_tracker):
        return self.metric_manager.reload_result_info(source_tracker.metric_manager)

    def get_output_data_info(self, data_name=None):
        return self.read_output_data_info_from_db(data_name=data_name)

    def read_output_data_info_from_db(self, data_name=None):
        filter_dict = {}
        filter_dict["job_id"] = self.job_id
        filter_dict["component_name"] = self.component_name
        filter_dict["role"] = self.role
        filter_dict["party_id"] = self.party_id
        if data_name:
            filter_dict["data_name"] = data_name
        return self.query_output_data_infos(**filter_dict)

    @classmethod
    @DB.connection_context()
    def query_output_data_infos(cls, **kwargs) -> typing.List[ResultDataInfoDTO]:
        try:
            #tracking_output_data_info_model = cls.get_dynamic_db_model(TrackingOutputDataInfo, kwargs.get("job_id"))
            filters = []
            for f_n, f_v in kwargs.items():
                #attr_name = 'f_%s' % f_n
                if hasattr(ResultDataInfoDTO, f_n):
                    filters.append(operator.attrgetter('%s' % f_n)(ResultDataInfoDTO) == f_v)
            if filters:
                output_data_infos_tmp = ResultDataInfoDTO.select().where(*filters).order_by(ResultDataInfoDTO.f_create_time.desc())
            else:
                output_data_infos_tmp = ResultDataInfoDTO.select()
            output_data_infos_group = {}
            # only the latest version of the task output data is retrieved
            for output_data_info in output_data_infos_tmp:
                group_key = cls.get_output_data_group_key(output_data_info.task_id, output_data_info.data_name)
                if group_key not in output_data_infos_group:
                    output_data_infos_group[group_key] = output_data_info
                elif output_data_info.task_version > output_data_infos_group[group_key].task_version:
                    output_data_infos_group[group_key] = output_data_info
            return list(output_data_infos_group.values())
        except Exception as e:
            LOGGER.exception(e)
            return []

    @classmethod
    def get_output_data_group_key(cls, task_id, data_name):
        return task_id + data_name

    def clean_task(self, sess, runtime_conf):
        LOGGER.info('clean task {} {} on {} {}'.format(self.task_id,
                                                                             self.task_version,
                                                                             self.role,
                                                                             self.party_id))
        try:
        
            # clean up temporary tables
            computing_temp_namespace = generate_session_id(task_id=self.task_id,
                                                                     task_version=self.task_version,
                                                                     role=self.role,
                                                                     party_id=self.party_id)
            try:
                if self.job_parameters.computing_engine != ComputingEngine.LINKIS_SPARK:
                    #sess.init_computing(computing_session_id=f"{computing_temp_namespace}_clean",
                    #                    options={})
                    sess.computing.cleanup(namespace=computing_temp_namespace, name="*")
                    LOGGER.info(
                        'clean table by namespace {} on {} {} done'.format(computing_temp_namespace,
                                                                           self.role,
                                                                           self.party_id))
                    # clean up the last tables of the federation
                    federation_temp_namespace = generate_task_version_id(self.task_id, self.task_version)
                    sess.computing.cleanup(namespace=federation_temp_namespace, name="*")
                    LOGGER.info(
                        'clean table by namespace {} on {} {} done'.format(federation_temp_namespace,
                                                                           self.role,
                                                                           self.party_id))
                if self.job_parameters.federation_engine == FederationEngine.RABBITMQ and self.role != "local":
                    LOGGER.info('rabbitmq start clean up')
                    parties = [Party(k, p) for k, v in runtime_conf['role'].items() for p in v]
                    federation_session_id = generate_task_version_id(self.task_id, self.task_version)
                    component_parameters_on_party = copy.deepcopy(runtime_conf)
                    component_parameters_on_party["local"] = {"role": self.role, "party_id": self.party_id}
                    #sess.init_federation(federation_session_id=federation_session_id,
                    #                     runtime_conf=component_parameters_on_party,
                    #                     service_conf=self.job_parameters.engines_address.get(EngineType.FEDERATION,
                    #                                                                          {}))
                    sess._federation_session.cleanup(parties)
                    LOGGER.info('rabbitmq clean up success')

                # TODO optimize the clean process
                if self.job_parameters.federation_engine == FederationEngine.PULSAR and self.role != "local":
                    LOGGER.info('start to clean up pulsar topics')
                    parties = [Party(k, p) for k, v in runtime_conf['role'].items() for p in v]
                    federation_session_id = generate_task_version_id(self.task_id, self.task_version)
                    component_parameters_on_party = copy.deepcopy(runtime_conf)
                    component_parameters_on_party["local"] = {"role": self.role, "party_id": self.party_id}
                    #sess.init_federation(federation_session_id=federation_session_id,
                    #                     runtime_conf=component_parameters_on_party,
                    #                     service_conf=self.job_parameters.engines_address.get(EngineType.FEDERATION,
                    #                                                                          {}))
                    sess.federation.cleanup(parties)
                    LOGGER.info('pulsar topic clean up success')
            except Exception as e:
                LOGGER.exception("cleanup error")
            finally:
                sess.destroy_all_sessions()
            return True
        except Exception as e:
            LOGGER.exception(e)
            return False

    # @DB.connection_context()
    # def save_machine_learning_model_info(self):
    #     try:
    #         record = MLModel.get_or_none(MLModel.f_model_version == self.job_id,
    #                                      MLModel.f_role == self.role,
    #                                      MLModel.f_model_id == self.model_id,
    #                                      MLModel.f_party_id == self.party_id)
    #         if not record:
    #             job = Job.get_or_none(Job.f_job_id == self.job_id)
    #             pipeline = self.pipelined_model.read_pipeline_model()
    #             if job:
    #                 job_data = job.to_dict()
    #                 model_info = {
    #                     'job_id': job_data.get("f_job_id"),
    #                     'role': self.role,
    #                     'party_id': self.party_id,
    #                     'roles': job_data.get("f_roles"),
    #                     'model_id': self.model_id,
    #                     'model_version': self.model_version,
    #                     'initiator_role': job_data.get('f_initiator_role'),
    #                     'initiator_party_id': job_data.get('f_initiator_party_id'),
    #                     'runtime_conf': job_data.get('f_runtime_conf'),
    #                     'work_mode': job_data.get('f_work_mode'),
    #                     'train_dsl': job_data.get('f_dsl'),
    #                     'train_runtime_conf': job_data.get('f_train_runtime_conf'),
    #                     'size': self.get_model_size(),
    #                     'job_status': job_data.get('f_status'),
    #                     'parent': pipeline.parent,
    #                     'fate_version': pipeline.fate_version,
    #                     'runtime_conf_on_party': json_loads(pipeline.runtime_conf_on_party),
    #                     'parent_info': json_loads(pipeline.parent_info),
    #                     'inference_dsl': json_loads(pipeline.inference_dsl)
    #                 }
    #                 model_utils.save_model_info(model_info)
    #
    #                 schedule_logger(self.job_id).info(
    #                     'save {} model info done. model id: {}, model version: {}.'.format(self.job_id,
    #                                                                                        self.model_id,
    #                                                                                        self.model_version))
    #             else:
    #                 schedule_logger(self.job_id).info(
    #                     'save {} model info failed, no job found in db. '
    #                     'model id: {}, model version: {}.'.format(self.job_id,
    #                                                               self.model_id,
    #                                                               self.model_version))
    #         else:
    #             schedule_logger(self.job_id).info('model {} info has already existed in database.'.format(self.job_id))
    #     except Exception as e:
    #         schedule_logger(self.job_id).exception(e)

    #@classmethod
    #def get_dynamic_db_model(cls, base, job_id):
    #    return type(base.model(table_index=cls.get_dynamic_tracking_table_index(job_id=job_id)))

    #@classmethod
    #def get_dynamic_tracking_table_index(cls, job_id):
    #    return job_id[:8]

    def get_model_size(self):
        return self.pipelined_model.calculate_model_file_size()