#
#  Created by yuyunfu
#   2022/9/15 
#
from common.common.base_utils import current_timestamp

from common.common.log import getLogger
from common.metastore.db_models import ResultSummary, DB

LOGGER = getLogger()
class ResultSummaryManager:
    def __init__(self, job_id, component_name, role, party_id, task_id, task_version):
        self.job_id = job_id
        self.component_name = component_name
        self.role = role
        self.party_id = party_id
        self.task_id = task_id
        self.task_version = task_version
        
    
    @DB.connection_context()
    def save_data(self, summary_data: dict):
        try:
            summary = ResultSummary()
            summary_find = summary.get_or_none(
                summary.job_id == self.job_id,
                summary.component_name == self.component_name,
                summary.role == self.role,
                summary.party_id == self.party_id,
                summary.task_id == self.task_id,
                summary.task_version == self.task_version
            )
            if summary_find:
                summary_find.summary = summary_data
                summary_find.f_update_time = current_timestamp()
                summary_find.save()
            else:
                ResultSummary.create(
                    job_id=self.job_id,
                    component_name=self.component_name,
                    role=self.role,
                    party_id=self.party_id,
                    task_id=self.task_id,
                    task_version=self.task_version,
                    summary=summary_data,
                    create_time=current_timestamp()
                )
        except Exception as e:
            LOGGER.exception("An exception where querying summary job id: {} "
                             "component name: {} to database:\n{}".format(
                self.job_id, self.component_name, e)
            )
    
    @DB.connection_context()
    def read_data(self):
        try:
            summary = ResultSummary()
            summary_find = summary.get_or_none(
                summary.job_id == self.job_id,
                summary.component_name == self.component_name,
                summary.role == self.role,
                summary.party_id == self.party_id
            )
            if summary_find:
                return summary.summary
            else:
                return ""
        except Exception as e:
            LOGGER.exception(e)
            raise e
    
