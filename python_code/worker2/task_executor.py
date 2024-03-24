import argparse
import importlib
import json
import os
import sys
import traceback
from enum import Enum

from common import session
from common.common import file_utils, EngineType, log
from common.common.base_utils import current_timestamp
from common.common.file_utils import get_project_base_directory
from common.common.log import getLogger
from worker2.config.runtime_conf import Runtime, ExecRole
from worker2.entity.cache_data import CacheData
from worker2.entity.taskConfiguration import TaskConfiguration
from worker2.entity.taskInput import TaskInput
from worker2.entity.type import DataType
from worker2.management.result_manager import ResultManagement
from worker2.task_args import TaskExecArgs

LOGGER = getLogger()
#log.setDirectory(get_project_base_directory("log/worker"))

class TaskStatus(Enum):
    @classmethod
    def status_list(cls):
        return [cls.__dict__[k] for k in cls.__dict__.keys() if
                not callable(getattr(cls, k)) and not k.startswith("__")]
    
    @classmethod
    def contains(cls, status):
        return status in cls.status_list()
    
    WAITING = 'waiting'
    RUNNING = "running"
    CANCELED = "canceled"
    TIMEOUT = "timeout"
    FAILED = "failed"
    PASS = "pass"
    SUCCESS = "success"


class TaskExecutor():
    def __init__(self):
        self.args: TaskExecArgs = None
        self.run_pid = None
        self.report_info = {}
        
    def run(self, **kwargs):
        result = {}
        code = 0
        message = ""
        start_time = current_timestamp()
        self.run_pid = os.getpid()
        
        try:
            if (kwargs):
                self.args = TaskExecArgs(**kwargs)
            else:
                parser = argparse.ArgumentParser()
                for arg in TaskExecArgs().to_dict():
                    parser.add_argument(f"--{arg}", required=False)
                self.args = TaskExecArgs(**parser.parse_args().__dict__)
            #Runtime.init_env()
            
            #if not Runtime.LOAD_CONFIG_MANAGER:
                # JobDefaultConfig.load()
                # ServiceRegistry.load()
                # ResourceManager.initialize()
                #RuntimeConfig.load_config_manager()
            result = self._run()
        except Exception as e:
            LOGGER.exception(e)
            raise e
        finally:
            end_time = current_timestamp()
            LOGGER.info(f"Finish task executor, pid: {self.run_pid}, elapsed: {end_time - start_time} ms")
            if Runtime.EXEC_ROLE == ExecRole.WORKER:
                sys.exit(code)
            else:
                return code, message, result
    
    def _run(self):
        job_id = self.args.job_id
        component_name = self.args.component_name
        task_id = self.args.task_id
        role = self.args.role
        party_id = self.args.party_id
        run_pid = self.run_pid
        user_name = self.args.user
        
        run_inf = {
            "job_id": job_id,
            "component_name": component_name,
            "task_id": task_id,
            "role": role,
            "party_id": party_id,
            "run_pid": run_pid
        }
        
        self.report_info.update(run_inf)
        start_time = current_timestamp()
        LOGGER.info("start work")
        LOGGER.info(f'Start exec task {component_name} {task_id} about {role} {party_id} ')
        try:
            
            task_configuration = TaskConfiguration(task_param=self.args.task_param,
                                                   task_conf=self.args.task_conf, task_job=self.args.job_conf)
            
            run_inf.pop("run_pid")
            run_inf["model_id"] = task_configuration.model_id
            run_inf['model_version'] = task_configuration.model_version
            run_inf['component_module_name'] = task_configuration.module_name
            run_inf["task_version"] = self.args.task_version
            run_inf["task_configuration"] = task_configuration
            tracker = ResultManagement(**run_inf)
            
            self.report_info["party_status"] = TaskStatus.RUNNING
            
            # init environment, process is shared globally
            Runtime.init_config(COMPUTING_ENGINE=task_configuration.computing_engine,
                                FEDERATION_ENGINE=task_configuration.federation_engine,
                                FEDERATED_MODE=task_configuration.federated_mode)
            
            sess = session.Session(task_conf = self.args.task_conf)
            sess.as_global()
            sess.init_computing()
            
            sess.init_federation(federation_session_id=self.args.federation_session_id,
                                 runtime_conf=task_configuration.job_conf,
                                 service_conf=task_configuration.engines_address.get(EngineType.FEDERATION, {}))
            
            task_run_args, input_table_list = self.get_task_run_args(job_id=job_id, role=role,
                                                                     party_id=party_id,
                                                                     task_id=task_id,
                                                                     task_version=self.args.task_version,
                                                                     task_parameters=task_configuration,
                                                                     task_input=task_configuration.task_input)
            
            LOGGER.info(f"task input args {task_run_args}")
            
            cpn_input = TaskInput(
                monitor=tracker,
                checkpoint_manager=None,
                parameters=task_configuration.task_param.get("param"),
                datasets=task_run_args.get(DataType.DATA.value, None),
                caches=task_run_args.get(DataType.CACHE.value, None),
                models=dict(
                    model=task_run_args.get(DataType.MODEL.value),
                    isometric_model=task_run_args.get(DataType.ISO_MODEL.value),
                ),
                job_parameters=task_configuration,
                roles=dict(
                    role=task_configuration.roles,
                    local=task_configuration.local,
                ),
                task_version="{}_{}".format(self.args.task_id, self.args.task_version),
            )
            run_object = self.get_run_obj(task_configuration.module_name, role)
            
            cpn_output = run_object.run(cpn_input)
            sess.wait_remote_all_done()
            
            output_table_list = []
            LOGGER.info(f"task output data {cpn_output.data}")
            for index, data in enumerate(cpn_output.data):
                data_name = task_configuration.task_output.get('data')[index] if task_configuration.task_output.get(
                    'data') else '{}'.format(index)
                # todo: the token depends on the engine type, maybe in job parameters
                persistent_table_namespace, persistent_table_name = tracker.save_output_data(
                    computing_table=data,
                    output_storage_engine=task_configuration.storage_engine,
                    token={"username": user_name})
                if persistent_table_namespace and persistent_table_name:
                    tracker.log_output_data_info(data_name=data_name,
                                                 table_namespace=persistent_table_namespace,
                                                 table_name=persistent_table_name
                                                 )
                    output_table_list.append({"namespace": persistent_table_namespace, "name": persistent_table_name})
            
            # There is only one model output at the current dsl version.
            tracker.save_output_model(model_buffers=cpn_output.model,
                                      model_alias=task_configuration.task_output['model'][
                                          0] if task_configuration.task_output.get(
                                          'model') else 'default')
            
            if cpn_output.cache is not None:
                for i, cache in enumerate(cpn_output.cache):
                    if cache is None:
                        continue
                    name = task_configuration.task_output.get("cache")[
                        i] if "cache" in task_configuration.task_output else str(i)
                    if isinstance(cache, CacheData):
                        tracker.tracking_output_cache(cache, cache_name=name)
                    elif isinstance(cache, tuple):
                        tracker.save_output_cache(cache_data=cache[0],
                                                  cache_meta=cache[1],
                                                  cache_name=name,
                                                  output_storage_engine=task_configuration.storage_engine,
                                                  output_storage_address=task_configuration.engines_address.get(
                                                      EngineType.STORAGE, {}),
                                                  token={"username": user_name})
                    else:
                        raise RuntimeError(f"can not support type {type(cache)} module run object output cache")
            
            self.report_info["party_status"] = TaskStatus.SUCCESS
            #补救措施，为了清除未消费的pulsar消息，避免下次运行消费上次残留的消息
            tracker.clean_task(sess, task_configuration.job_conf)
        except Exception as e:
            traceback.print_exc()
            self.report_info["party_status"] = TaskStatus.FAILED
            LOGGER.exception(e)
            raise e
        finally:
            try:
               
                self.report_info["end_time"] = current_timestamp()
                self.report_info["elapsed"] = self.report_info["end_time"] - start_time
            except Exception as e:
                self.report_info["party_status"] = TaskStatus.FAILED
                traceback.print_exc()
                LOGGER.exception(e)
        
        return self.report_info
    
    def get_run_obj(self, module_name, role):
        component_root = os.path.join(file_utils.get_project_base_directory("python_code"), 'algorithm', 'feature')
        
        # federated_learning_type = runtime_conf["job"]["federated_learning_type"]
        module_name_dir = module_name.lower()
        
        if os.path.exists(os.path.join(component_root, module_name_dir)):
            component_full_path = os.path.join(component_root, module_name_dir)
        else:
            component_full_path = file_utils.match_dir(component_root, module_name_dir)
        
        if not component_full_path:
            raise Exception(f'{module_name}不存在!')
        
        code_path = self.get_code_path(component_full_path, module_name, role=role)
        run_class_paths = code_path.split('/')
        run_class_package = '.'.join(run_class_paths[:-2]) + '.' + run_class_paths[-2].replace('.py', '')
        run_class_name = run_class_paths[-1]
        
        run_object = getattr(importlib.import_module(run_class_package), run_class_name)()
        
        return run_object
    
    def get_code_path(self, component_full_path, module_name, role):
        _module_setting_path = os.path.join(component_full_path, "setting.json")
        _module_setting = None
        with open(_module_setting_path, "r") as fin:
            _module_setting = json.loads(fin.read())
        
        if not _module_setting:
            raise Exception("{} is not set in setting_conf ".format(module_name))
        
        # module_path = os.path.join('kernel', 'components', module.lower())
        module_path = component_full_path.replace(file_utils.get_project_base_directory(), '')[1:]
        
        _support_rols = _module_setting["role"].keys()
        _role_setting = None
        for _rolelist in _support_rols:
            if role in _rolelist.split("|"):
                _role_setting = _module_setting["role"].get(_rolelist)
        _code_path = os.path.join(module_path, _role_setting.get('program'))
        
        return _code_path
    
    @classmethod
    def get_task_run_args(cls, job_id, role, party_id, task_id, task_version,
                          task_parameters: TaskConfiguration,
                          task_input):
        task_run_args = {}
        input_table_info_list = []
        
        for input_type, input_detail in task_input.items():
            if input_type == DataType.DATA.value:
                data, table = cls.get_task_data_args(input_detail, job_id, role, party_id,task_id,task_version, task_parameters)
                task_run_args.update( data)
                input_table_info_list += table
            elif input_type == DataType.CACHE.value:
                this_type_args = task_run_args[input_type] = task_run_args.get(input_type, {})
                for search_key in input_detail:
                    search_component_name, cache_name = search_key.split(".")
                    tracker = ResultManagement(job_id=job_id, role=role, party_id=party_id,
                                               component_name=search_component_name)
                    this_type_args[search_component_name] = tracker.get_output_cache(cache_name=cache_name)
            elif input_type in {DataType.MODEL.value, DataType.ISO_MODEL.value}:
                this_type_args = task_run_args[input_type] = task_run_args.get(input_type, {})
                for dsl_model_key in input_detail:
                    dsl_model_key_items = dsl_model_key.split('.')
                    if len(dsl_model_key_items) == 2:
                        search_component_name, search_model_alias = dsl_model_key_items[0], dsl_model_key_items[1]
                    elif len(dsl_model_key_items) == 3 and dsl_model_key_items[0] == 'pipeline':
                        search_component_name, search_model_alias = dsl_model_key_items[1], dsl_model_key_items[2]
                    else:
                        raise Exception('get input {} failed'.format(input_type))
                    
                    tracker = ResultManagement(job_id=job_id, role=role, party_id=party_id,
                                               component_name=search_component_name,
                                               model_id=task_parameters.model_id,
                                               model_version=task_parameters.model_version)
                    models = tracker.read_output_model(search_model_alias)
                    this_type_args[search_component_name] = models
            else:
                raise Exception(f"not support {input_type} input type")
        
        return task_run_args, input_table_info_list

    @classmethod
    def get_task_data_args(cls, input_detail, job_id, role, party_id, task_id, task_version, task_parameters):
        task_run_args = {}
        input_table_info_list = []
        
        this_type_args = task_run_args[DataType.DATA.value] = task_run_args.get(DataType.DATA.value, {})
        for data_type, data_list in input_detail.items():
            data_dict = {}
            for data_key in data_list:
                data_key_item = data_key.split('.')
                data_dict[data_key_item[0]] = {data_type: []}
            for data_key in data_list:
                data_key_item = data_key.split('.')
                search_component_name, search_data_name = data_key_item[0], data_key_item[1]
                storage_table_meta = None
                tracker = ResultManagement(job_id=job_id, role=role, party_id=party_id,
                                           component_name=search_component_name,
                                           task_id=task_id, task_version=task_version)
                pre_output_table_infos = tracker.get_output_data_info(
                    data_name=search_data_name)
                if pre_output_table_infos:
                    # upstream_output_table_infos = []
                
                    # for _ in upstream_output_table_infos_json:
                    #     upstream_output_table_infos.append(fill_db_model_object(
                    #         Tracker.get_dynamic_db_model(TrackingOutputDataInfo, job_id)(), _))
                    output_tables_meta = tracker.get_output_data_table(pre_output_table_infos)
                    if output_tables_meta:
                        storage_table_meta = output_tables_meta.get(search_data_name, None)
                args_from_component = this_type_args[search_component_name] = this_type_args.get(
                    search_component_name, {})
            
                if storage_table_meta:
                    LOGGER.info(f"load computing table use {task_parameters.computing_partitions}")
                    computing_table = session.get_computing_session().load(
                        storage_table_meta.get_address(),
                        schema=storage_table_meta.get_schema(),
                        partitions=task_parameters.computing_partitions)
                    input_table_info_list.append({'namespace': storage_table_meta.get_namespace(),
                                                  'name': storage_table_meta.get_name()})
                else:
                    computing_table = None
            
                data_dict[search_component_name][data_type].append(computing_table)
                args_from_component[data_type] = data_dict[search_component_name][data_type]

        return task_run_args, input_table_info_list
    
if __name__ == '__main__':
    worker = TaskExecutor()
    worker.run()