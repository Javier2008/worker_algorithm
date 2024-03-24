import os
import uuid

from common.common import file_utils
from common.common._types import InputSearchType
from common.storage import StorageEngine


def default_output_info(task_id, task_version, output_type):
    return f"output_{output_type}_{task_id}_{task_version}", uuid.uuid1().hex


def default_input_fs_path(name, namespace, prefix=None, storage_engine=StorageEngine.HDFS):
    if storage_engine == StorageEngine.HDFS:
        return default_hdfs_path(data_type="input", name=name, namespace=namespace, prefix=prefix)
    elif storage_engine == StorageEngine.LOCALFS:
        return default_localfs_path(data_type="input", name=name, namespace=namespace)


def default_output_fs_path(name, namespace, prefix=None, storage_engine=StorageEngine.HDFS):
    if storage_engine == StorageEngine.HDFS:
        return default_hdfs_path(data_type="output", name=name, namespace=namespace, prefix=prefix)
    elif storage_engine == StorageEngine.LOCALFS:
        return default_localfs_path(data_type="output", name=name, namespace=namespace)


def default_localfs_path(name, namespace, data_type):
    return os.path.join(file_utils.get_project_base_directory(), 'localfs', data_type, namespace, name)


def default_hdfs_path(data_type, name, namespace, prefix=None):
    p = f"/hdfs/{data_type}_data/{namespace}/{name}"
    if prefix:
        p = f"{prefix}/{p}"
    return p

def get_input_search_type(parameters):
    if "name" in parameters and "namespace" in parameters:
        return InputSearchType.TABLE_INFO
    elif "job_id" in parameters and "component_name" in parameters and "data_name" in parameters:
        return InputSearchType.JOB_COMPONENT_OUTPUT
    else:
        return InputSearchType.UNKNOWN
    
def get_header_schema(header_line, id_delimiter, extend_sid=False):
    header_source_item = header_line.split(id_delimiter)
    if extend_sid:
        header = id_delimiter.join(header_source_item).strip()
        sid = "sid"
    else:
        header = id_delimiter.join(header_source_item[1:]).strip()
        sid = header_source_item[0].strip()
    return {'header': header, 'sid': sid}