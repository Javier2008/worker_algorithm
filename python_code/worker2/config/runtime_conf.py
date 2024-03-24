
from enum import Enum


class ExecRole(Enum):
    DRIVER = "driver"
    WORKER = "worker"
    
class Runtime():
    DEBUG = None
    WORK_MODE = None
    COMPUTING_ENGINE = None
    FEDERATION_ENGINE = None
    FEDERATED_MODE = None

    JOB_QUEUE = None
    USE_LOCAL_DATABASE = False
    HTTP_PORT = None
    JOB_SERVER_HOST = None
    JOB_SERVER_VIP = None
    IS_SERVER = False
    EXEC_ROLE = ExecRole.WORKER
    ENV = dict()
    COMPONENT_PROVIDER = None
    SERVICE_DB = None
    LOAD_COMPONENT_REGISTRY = False
    LOAD_CONFIG_MANAGER = False

    @classmethod
    def init_config(cls, **kwargs):
        for k, v in kwargs.items():
            if hasattr(cls, k):
                setattr(cls, k, v)

    #@classmethod
    #def init_env(cls):
    #    cls.ENV.update(get_versions())

    @classmethod
    def load_component_registry(cls):
        cls.LOAD_COMPONENT_REGISTRY = True

    @classmethod
    def load_config_manager(cls):
        cls.LOAD_CONFIG_MANAGER = True

    @classmethod
    def get_env(cls, key):
        return cls.ENV.get(key, None)

    @classmethod
    def get_all_env(cls):
        return cls.ENV

    @classmethod
    def set_exec_role(cls, exec_role):
        cls.EXEC_ROLE = exec_role

    @classmethod
    def set_component_provider(cls, component_provider):
        cls.COMPONENT_PROVIDER = component_provider

    @classmethod
    def set_service_db(cls, service_db):
        cls.SERVICE_DB = service_db
        
    @classmethod
    def get_all(cls):
        configs = {}
        for k, v in cls.__dict__.items():
            if not callable(getattr(cls, k)) and not k.startswith("__") and not k.startswith("_"):
                configs[k] = v
        return configs

    @classmethod
    def get(cls, config_name):
        return getattr(cls, config_name) if hasattr(cls, config_name) else None
