#
#  Created by yuyunfu
#   2022/9/9 
#

class TaskInput:
    def __init__(
            self,
            monitor,
            checkpoint_manager,
            parameters,
            datasets,
            models,
            caches,
            job_parameters,
            roles,
            task_version
    ) -> None:
        self._monitor = monitor
        self._checkpoint_manager = checkpoint_manager
        self._parameters = parameters
        self._datasets = datasets
        self._models = models
        self._caches = caches
        self._job_parameters = job_parameters
        self._roles = roles
        self._task_version = task_version

    @property
    def tracker(self):
        return self._monitor

    @property
    def checkpoint_manager(self):
        return self._checkpoint_manager

    @property
    def parameters(self):
        return self._parameters

    @property
    def roles(self):
        return self._roles

    @property
    def job_parameters(self):
        return self._job_parameters

    @property
    def datasets(self):
        return self._datasets

    @property
    def models(self):
        return {k: v for k, v in self._models.items() if v is not None}

    @property
    def caches(self):
        return self._caches

    @property
    def task_version_id(self):
        return self._task_version