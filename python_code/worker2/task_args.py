import json

from common.common.log import getLogger

LOGGER = getLogger()


class TaskExecArgs():
    def __init__(self, **kwargs):
        self.job_id = kwargs.get("job_id")
        self.component_name = kwargs.get("component_name")
        self.task_id = kwargs.get("task_id")
        self.role = kwargs.get("role")
        self.party_id = kwargs.get("party_id")
        self.result = kwargs.get("result")
        self.log_dir = kwargs.get("log_dir")
        self.parent_log_dir = kwargs.get("parent_log_dir")
        self.user = kwargs.get("user")
        self.worker_id = kwargs.get("worker_id")
        self.federation_session_id = kwargs.get("federation_session_id")
        self.task_version = kwargs.get("task_version")
        
        # conf
        if kwargs:
            s =kwargs.get("task_conf")
            print(s)
            self.task_conf = json.loads(s)
            self.task_param = json.loads(kwargs.get("task_param"))
            self.job_conf = json.loads(kwargs.get("job_conf"))
        else:
            self.task_conf = None
            self.task_param = None
            self.job_conf = None
            
        self.session_id = kwargs.get("session_id")
        
    def to_dict(self):
        return dict([(k.lstrip("_"), v) for k, v in self.__dict__.items()])