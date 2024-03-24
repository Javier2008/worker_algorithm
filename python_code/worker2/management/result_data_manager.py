#
#  Created by yuyunfu
#   2022/9/9 
#
import uuid

from common import storage
from common.common.base_utils import current_timestamp
from common.common.log import getLogger
from common.metastore.db_models import DB, ResultDataInfoDTO
from common.session import get_session

LOGGER = getLogger()


class ResultDataManager:
    def __init__(self, task_id: str, job_id: str, component_name: str, task_version:int, party_id:int, role:str):
        self.task_id = task_id
        self.job_id = job_id
        self.component_name = component_name
        self.task_version = task_version
        self.party_id = party_id
        self.role = role
        self.output_data_summary_count_limit =  100
        
    def save_data(self, computing_table, storage_engine, storage_address=None,
                  table_namespace=None, table_name=None, schema=None, token=None, need_read=True):
        if computing_table:
            if not table_namespace or not table_name:
                table_namespace = f"result_data_{self.task_id}"
                table_name = uuid.uuid1().hex
            
            part_of_limit = self.output_data_summary_count_limit
            part_of_data = []
            if need_read:
                match_id_name = computing_table.schema.get("match_id_name")
                LOGGER.info(f'match id name:{match_id_name}')
                for k, v in computing_table.collect():
                    part_of_data.append((k, v))
                    part_of_limit -= 1
                    if part_of_limit == 0:
                        break

            LOGGER.info('save result data to {} {}'.format(table_namespace, table_name))
            
            get_session().persistent(computing_table=computing_table,
                                     namespace=table_namespace,
                                     name=table_name,
                                     schema=schema,
                                     part_of_data=part_of_data,
                                     engine=storage_engine,
                                     engine_address=storage_address,
                                     token=token)
            
            return table_namespace, table_name
        else:
            LOGGER.warn('save result data with none')
            return None, None
    
    def read_data_table(self, table_infos):
        output_tables_meta = {}
        if table_infos:
            for table_info in table_infos:
                LOGGER.info("Read data table {} {} for task {}".format(table_info.table_namespace,
                                                                       table_info.table_name,table_info.task_id))
                data_table_meta = storage.StorageTableMeta(name= table_info.table_name,
                                                           namespace= table_info.table_namespace)
                
                output_tables_meta[table_info.data_name] = data_table_meta
        return output_tables_meta
    
    @DB.connection_context()
    def save_data_info(self, data_name: str, table_namespace: str, table_name: str):
        try:
            data_info = ResultDataInfoDTO()
            data_info.job_id = self.job_id
            data_info.component_name = self.component_name
            data_info.task_id = self.task_id
            data_info.task_version = self.task_version
            data_info.data_name = data_name
            data_info.table_namespace = table_namespace
            data_info.table_name = table_name
            data_info.party_id = self.party_id
            data_info.role = self.role
            data_info.f_create_time = current_timestamp()
            self.insert_into_db(ResultDataInfoDTO,
                                     [data_info.to_dict()])
        except Exception as e:
            LOGGER.exception(
                "save data info {} {} {} to database:\n{}".format(
                    data_name,
                    table_namespace,
                    table_name,
                    e
                ))
            raise Exception(e)
    
    @DB.connection_context()
    def insert_into_db(self, model, data_source):
        try:
            batch_size =  1000
            for i in range(0, len(data_source), batch_size):
                with DB.atomic():
                    model.insert_many(data_source[i:i + batch_size]).execute()
            return len(data_source)
        except Exception as e:
            LOGGER.exception(e)
            return 0
