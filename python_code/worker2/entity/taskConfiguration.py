#
#  Created by yuyunfu
#   2022/9/9 
#


class TaskConfiguration:
    def __init__(self, **kwargs):
        self._job_conf = kwargs.get("task_job")
        self._task_conf = kwargs.get("task_conf")
        self._task_param = kwargs.get("task_param")
        
        self.job_type = "train"
        self.inheritance_info = {}  # job_id, component_list
        self.computing_engine = None
        self.federation_engine = None
        self.storage_engine = None
        self.engines_address = {}
        self.federated_mode = None
        self.federation_info = None
        self.task_cores = None
        self.task_parallelism = None
        self.computing_partitions = None
        self.federated_status_collect_type = None
        self.federated_data_exchange_type = None  # not use in v1.5.0
        self.model_id = None
        self.model_version = None
        self.auto_retries = None
        self.auto_retry_delay = None
        self.timeout = None
        self.spark_run = {}
        self.pulsar_run = {}
        self.adaptation_parameters = {}
        self.assistant_role = None
        self.map_table_name = None
        self.map_namespace = None
        
        self.param = None
        self.init()
    
    def init(self):
        for k, v in self._task_conf.items():
            if hasattr(self, k):
                setattr(self, k, v)
        
        self.computing_engine = self._task_conf.get("computing")
        self.federation_engine = self._task_conf.get("federation")
        self.storage_engine = self._task_conf.get("storage")
        
        for k, v in self._task_param.items():
            if hasattr(self, k):
                setattr(self, k, v)
    @property
    def module_name(self):
        return self._task_param.get("module")
    
    @property
    def task_input(self):
        return self._task_param.get("input")
    
    @property
    def task_output(self):
        return self._task_param.get("output")
    
    @property
    def job_conf(self):
        return self._job_conf
    
    @property
    def task_conf(self):
        return self._task_conf
    
    @property
    def task_param(self):
        return self._task_param

    @property
    def local(self):
        return self._job_conf.get("local")

    @property
    def roles(self):
        return self._job_conf.get("role")

    
if __name__ == '__main__':
    job_conf = {
        "job_type": "train",
        "initiator": {
            "role": "guest",
            "party_id": 9999
        },
        "role": {
            "arbiter": [
                10000
            ],
            "host": [
                10000
            ],
            "guest": [
                9999
            ]
        },
        "local": {
            "role": "host",
            "party_id": 10000
        },
    }
    task_conf = {
        "inheritance_info": {},
        "computing_engine": "STANDALONE",
        "federation_engine": "STANDALONE",
        "storage_engine": "STANDALONE",
        "engines_address": {
            "computing": {
                "cores_per_node": 20,
                "nodes": 1
            },
            "federation": {
                "cores_per_node": 20,
                "nodes": 1
            },
            "storage": {
                "cores_per_node": 20,
                "nodes": 1
            }
        },
        "federated_mode": "SINGLE",
        "task_cores": 1,
        "computing_partitions": 1,
        "adaptation_parameters": {
            "task_nodes": 1,
            "task_cores_per_node": 1,
            "task_memory_per_node": 0,
            "request_task_cores": 1,
            "if_initiator_baseline": False
        },
        "src_user": None
    }
    task_param = {
        "module": "DataIO",
        "CodePath": "hetero_feature_binning",
        "model_id": "arbiter-10000#guest-9999#host-10000#model",
        "model_version": "302208311458578984881",
        "input": {
            "data": {
                "data": ["reader_0.data"]
            }
        },
        "output": {
            "data": [
                "data"
            ],
            "model": [
                "model"
            ]
        },
        "param": {
            "missing_fill": True,
            "missing_fill_method": "mean",
            "outlier_replace": False,
            "outlier_replace_method": "designated",
            "outlier_impute": "-9999",
            "outlier_replace_value": 0.66,
            "with_label": False,
            "label_name": "label",
            "label_type": "int",
            "output_format": "dense"
        }
    }
    
    t = TaskConfiguration(task_conf=task_conf, task_param=task_param, job_conf=job_conf)
    print(t.task_output)
