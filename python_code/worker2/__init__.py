from functools import wraps
from pathlib import Path

from filelock import FileLock


class Locker:

    def __init__(self, directory):
        if isinstance(directory, str):
            directory = Path(directory)
        self.directory = directory
        self.lock = self._lock

    @property
    def _lock(self):
        return FileLock(self.directory / '.lock')

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self

    # https://docs.python.org/3/library/pickle.html#handling-stateful-objects
    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop('lock')
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.lock = self._lock
        
def local_cache_required(method):
    @wraps(method)
    def magic(self, *args, **kwargs):
        if not self.exists():
            raise FileNotFoundError(f'Can not found {self.model_id} {self.model_version} model local cache')
        return method(self, *args, **kwargs)
    return magic