#
#  Created by yuyunfu
#   2022/9/13 
#
import typing

from common.common import DTable


class CacheData:
    def __init__(self, name: str, key: str = None, data: typing.Dict[str, DTable] = None, meta: dict = None, job_id: str = None, task_id: str = None, task_version: int = 0, component_name: str = None):
        self._name = name
        self._key = key
        self._data = data if data else {}
        self._meta = meta
        
        self._job_id = job_id
        self._task_id  = task_id
        self._task_version = task_version
        self._component_name = component_name
        

    @property
    def name(self):
        return self._name

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, key: str):
        self._key = key

    @property
    def data(self):
        return self._data

    @property
    def meta(self):
        return self._meta

    @property
    def job_id(self):
        return self._job_id

    @job_id.setter
    def job_id(self, job_id: str):
        self._job_id = job_id

    @property
    def component_name(self):
        return self._component_name

    @component_name.setter
    def component_name(self, component_name: str):
        self._component_name = component_name

    @property
    def task_id(self):
        return self._task_id

    @task_id.setter
    def task_id(self, task_id: str):
        self._task_id = task_id

    @property
    def task_version(self):
        return self._task_version
