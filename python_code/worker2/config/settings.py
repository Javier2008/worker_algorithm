#
#  Created by yuyunfu
#   2022/9/9 
#
import os

from common.common.conf_utils import decrypt_database_config
from common.common.file_utils import get_project_base_directory

DATABASE_CONF = decrypt_database_config()

TEMP_DIRECTORY = os.path.join(get_project_base_directory(), "temp")

def job_component_name():
    return "job"


def job_component_module_name():
    return "Job"
