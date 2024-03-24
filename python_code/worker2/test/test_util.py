#
#  Created by yuyunfu
#   2022/10/11 
#
import os
import subprocess
import sys
import uuid

from common.common.file_utils import get_project_base_directory
from common.common.log import getLogger

logger = getLogger()

def get_std_path(log_dir, process_name="", process_id=""):
    std_log_path = f"{process_name}_{process_id}_std_log" if process_name else "std_log"
    return os.path.join(log_dir, std_log_path)

def run_subprocess(job_id, config_dir, process_cmd, added_env: dict = None, log_dir=None, cwd_dir=None, process_name="", process_id=""):
    process_cmd = [str(cmd) for cmd in process_cmd]
    logger.info("start process command: \n{}".format(" ".join(process_cmd)))

    os.makedirs(config_dir, exist_ok=True)
    if not log_dir:
        log_dir = config_dir
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    std_path = get_std_path(log_dir=log_dir, process_name=process_name, process_id=process_id)
    std = open(std_path, 'w')
    pid_path = os.path.join(config_dir, f"{process_name}_pid")

    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
    else:
        startupinfo = None

    subprocess_env = os.environ.copy()
    subprocess_env["PROCESS_ROLE"] = "worker"
    if added_env:
        for name, value in added_env.items():
            if name.endswith("PATH"):
                subprocess_env[name] = f"{value}:{subprocess_env.get(name, '')}".rstrip(':')
            else:
                subprocess_env[name] = value
    subprocess_env.pop("CLASSPATH", None)

    p = subprocess.Popen(process_cmd,
                         stdout=std,
                         stderr=std,
                         startupinfo=startupinfo,
                         cwd=cwd_dir,
                         env=subprocess_env
                         )
    with open(pid_path, 'w') as f:
        f.truncate()
        f.write(str(p.pid) + "\n")
        f.flush()
    logger.info(f"start process successfully, pid: {p.pid}, std log path: {std_path}")
    p.wait(100)
    return p

def get_process_dirs(task):
    worker_id = uuid.uuid1().hex

    config_dir = os.path.join(get_project_base_directory(), 'jobs', task.get("job_id"), task.get("role"),  task.get("party_id"),
                                      task.get("component_name"), task.get("task_id"),
                                             str(task.get("task_version")),  worker_id)
    log_dir = os.path.join(get_project_base_directory(), 'logs', task.get("job_id"), task.get("role"),
                           task.get("party_id"), task.get("component_name"))
    
    os.makedirs(config_dir, exist_ok=True)
    return worker_id, config_dir, log_dir
    
def start_task_worker(task: dict,
                      executable: list = None, extra_env: dict = None, **kwargs):
    worker_id, config_dir, log_dir = get_process_dirs(task)

    session_id = "{}_{}_{}_{}".format(task.get("task_id"), task.get("task_version"), task.get("role"), task.get("party_id"))
    federation_session_id = "{}_{}".format(task.get("task_id"), task.get("task_version"))

    info_kwargs = {}
    specific_cmd = []
    
    from worker2.task_executor import TaskExecutor
    module_file_path = sys.modules[TaskExecutor.__module__].__file__


    if executable:
        process_cmd = executable
    else:
        process_cmd = [sys.executable or "python3"]

    common_cmd = [
        module_file_path,
        "--job_id", task.get("job_id"),
        "--component_name", task.get("component_name"),
        "--task_id", task.get("task_id"),
        "--task_version", task.get("task_version"),
        "--role", task.get("role"),
        "--party_id", task.get("party_id"),
        "--task_conf", task.get("task_conf"),
        "--task_param", task.get("task_param"),
        "--job_conf", task.get("job_conf"),
        "--federation_session_id", federation_session_id,
        "--session_id", session_id,
        "--user", "Javier"
    ]
    process_cmd.extend(common_cmd)
    process_cmd.extend(specific_cmd)

    p = run_subprocess(job_id=task.get("job_id"), config_dir=config_dir, process_cmd=process_cmd,
                                     added_env=extra_env, log_dir=log_dir, cwd_dir=config_dir, process_name="worker",
                                     process_id=worker_id)
    return {"run_pid": p.pid, "worker_id": worker_id, "cmd": process_cmd}