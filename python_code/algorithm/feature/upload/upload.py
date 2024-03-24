# Copyright 2021 Tianmian Tech. All Rights Reserved.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Copyright 2019 The FATE Authors. All Rights Reserved.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import time
import uuid

from algorithm.model_base import ModelBase
from common import session, storage
from common.common import log, file_utils, data_utils
from common.common.data_utils import default_input_fs_path
from common.session import get_session
from common.storage import StorageEngine, StorageTableOrigin

# from fate_flow.entity.metric import Metric, MetricMeta

LOGGER = log.getLogger()

namespace_separator = '#'


def all_party_key(all_party):
    if not all_party:
        all_party_key = 'all'
    elif isinstance(all_party, dict):
        sorted_role_name = sorted(all_party.keys())
        all_party_key = namespace_separator.join([
            ('%s-%s' % (
                role_name,
                '_'.join([str(p) for p in sorted(set(all_party[role_name]))]))
             )
            for role_name in sorted_role_name])
    else:
        all_party_key = None
    return all_party_key


def get_table_info(config, create=False):
    table_name, namespace, role, member_id, all_party, data_type = config.get('table_name'), \
                                                                   config.get('namespace'), \
                                                                   config.get('local', {}).get('role'), \
                                                                   config.get('local', {}).get('member_id'), \
                                                                   config.get('role'), \
                                                                   config.get('data_type')
    if not config.get('gen_table_info', False):
        return table_name, namespace
    if not namespace:
        namespace = namespace_separator.join([role, str(member_id), all_party_key(all_party), data_type])
    if not table_name:
        if create:
            table_name = uuid.uuid1().hex
        else:
            raise Exception("don't support")
    return table_name, namespace


class Upload(ModelBase):
    def __init__(self):
        super().__init__()
        self.taskid = ''
        self.tracker = None
        self.MAX_PARTITION_NUM = 1024
        self.MAX_BYTES = 1024 * 1024 * 8
        self.parameters = {}
        self.id_index = 0
        self.table = None
        if not get_session():
            self.session = session.Session()
        else:
            self.session = get_session()
    
    def run(self, component_parameters=None, args=None):
        self.parameters = component_parameters["fileinfo"]
        self.id_index = component_parameters.get("id_index", 0)
        # self.parameters["role"] = component_parameters["role"]
        # self.parameters["local"] = component_parameters["local"]
        # storage_engine = self.parameters["storage_engine"].upper()
        # storage_address = self.parameters["storage_address"]
        
        job_id = self.taskid.split("_")[0]
        if not os.path.isabs(self.parameters.get("file", "")):
            self.parameters["file"] = os.path.join(file_utils.get_project_base_directory(), self.parameters["file"])
        if not os.path.exists(self.parameters["file"]):
            raise Exception("%s is not exist, please check the configure" % (self.parameters["file"]))
        table_name, namespace = get_table_info(config=self.parameters,
                                               create=True)
        _namespace, _table_name = self.generate_table_name(self.parameters["file"])
        if namespace is None:
            namespace = _namespace
        if table_name is None:
            table_name = _table_name
        read_head = self.parameters['head']
        if read_head == 0:
            head = False
        elif read_head == 1:
            head = True
        else:
            raise Exception("'head' in conf.json should be 0 or 1")
        partition = self.parameters["partition"]
        if partition <= 0 or partition >= self.MAX_PARTITION_NUM:
            raise Exception("Error number of partition, it should between %d and %d" % (0, self.MAX_PARTITION_NUM))
        
        # wingo: check if repeat upload
        self.prevent_repeat_upload(table_name, namespace)
        
        self.create_table(table_name, namespace, partition)
        data_table_count = self.save_data_table(self.id_index, head)
        LOGGER.info("------------load data finish!-----------------")
        LOGGER.info("file: {}".format(self.parameters["file"]))
        LOGGER.info("total data_count: {}".format(data_table_count))
        LOGGER.info("table name: {}, table namespace: {}".format(table_name, namespace))
    
    def create_table(self, name, namespace, partitions):
        storage_session = self.session.storage(record=False)
        storage_engine = storage_session.engine
        upload_address = {}
        if storage_engine in { StorageEngine.STANDALONE}:
            upload_address = {
                "name": name,
                "namespace": namespace
            }
        elif storage_engine in {StorageEngine.MYSQL, StorageEngine.HIVE}:
            upload_address = {"db": namespace, "name": name}
        elif storage_engine in {StorageEngine.PATH}:
            upload_address = {"path": self.parameters["file"]}
        elif storage_engine in {StorageEngine.HDFS}:
            upload_address = {
                "path": default_input_fs_path(
                    name=name,
                    namespace=namespace
                )
            }
        elif storage_engine in {StorageEngine.LOCALFS}:
            upload_address = {
                "path": default_input_fs_path(
                    name=name,
                    namespace=namespace,
                    storage_engine=storage_engine
                )
            }
        else:
            raise RuntimeError(f"can not support this storage engine: {storage_engine}")
        LOGGER.info(f"upload to {storage_engine} storage, address: {upload_address}")
        address = storage.StorageTableMeta.create_address(
            storage_engine=storage_engine, address_dict=upload_address
        )
        self.parameters["partitions"] = partitions
        self.parameters["name"] = name
        self.table = storage_session.create_table(address=address, origin=StorageTableOrigin.UPLOAD, **self.parameters)

        table_count = self.table.count()
        self.table.meta.update_metas(
            count=table_count,
            partitions=self.parameters["partition"],
            extend_sid=self.parameters["extend_sid"],
        )
        # self.save_meta(
        #     dst_table_namespace=namespace,
        #     dst_table_name=name,
        #     table_count=table_count,
        # )
        self.table.meta.update_metas(in_serialized=True)
        
    def set_taskid(self, taskid):
        self.taskid = taskid
    
    def set_tracker(self, tracker):
        self.tracker = tracker
    
    def save_data_table(self,  id_index=0, head=True):
        input_file = self.parameters["file"]
        count = self.get_count(input_file)
        with open(input_file, 'r') as fin:
            lines_count = 0
            if head is True:
                data_head = fin.readline()
                count -= 1
                self.save_data_header(data_head, id_index)
            while True:
                data = list()
                lines = fin.readlines(self.MAX_BYTES)
                if lines:
                    for line in lines:
                        values = line.replace("\n", "").replace("\t", ",").split(",")
                        if id_index == 0:
                            data.append((values[0], self.list_to_str(values[1:])))
                        elif id_index == len(values) - 1:
                            data.append((values[id_index], self.list_to_str(values[0: id_index])))
                        else:
                            data.append((values[id_index], self.list_to_str(values[0:id_index], values[id_index+1:])))
                    lines_count += len(data)
                    f_progress = lines_count / count * 100 // 1
                    job_info = {'f_progress': f_progress}
                    # self.update_job_status(self.parameters["local"]['role'], self.parameters["local"]['member_id'],
                    #                       job_info)
                    data_table = self._save_data(data)
                else:
                    # self.tracker.save_data_view(role=self.parameters["local"]['role'],
                    #                             member_id=self.parameters["local"]['member_id'],
                    #                             data_info={'f_table_name': dst_table_name,
                    #                                        'f_table_namespace': dst_table_namespace,
                    #                                        'f_partition': self.parameters["partition"],
                    #                                        'f_table_create_count': data_table.count()
                    #                                        })
                    # self.callback_metric(metric_name='data_access',
                    #                      metric_namespace='upload',
                    #                      metric_data=[Metric("count", data_table.count())])
                    return data_table.count()
    
    def _save_data(self, data):
        self.table.put_all(data)
        return self.table
    
    def save_data_header(self, header_source, id_index = 0):
        header_names = header_source.split(",")
        new_headers = [header_names[id_index]] + header_names[0:id_index] + header_names[id_index+1:]
        header_source = ",".join(new_headers)
            
        _, meta = self.table.meta.update_metas(
            schema=data_utils.get_header_schema(
                header_line=header_source,
                id_delimiter=self.parameters["id_delimiter"],
                extend_sid=self.parameters["extend_sid"],
            ),
            auto_increasing_sid=self.parameters["auto_increasing_sid"],
            extend_sid=self.parameters["extend_sid"],
        )
        self.table.meta = meta
    
    def get_count(self, input_file):
        with open(input_file, 'r', encoding='utf-8') as fp:
            count = 0
            for line in fp:
                count += 1
        return count
    
    def update_job_status(self, role, member_id, job_info):
        pass
        # self.tracker.save_job_info(role=role, member_id=member_id, job_info=job_info)
    

    def list_to_str(self, input_list1, input_list2 = None):
        if input_list2 is None:
            return ','.join(list(map(str, input_list1)))
        
        return ','.join(list(map(str, input_list1))) + "," + ','.join(list(map(str, input_list2)))
    
    def generate_table_name(self, input_file_path):
        str_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
        file_name = input_file_path.split(".")[0]
        file_name = file_name.split("/")[-1]
        return file_name, str_time
    
    def save_data(self):
        return None
    
    def output_data(self):
        return None
    
    def export_model(self):
        return None
    
    @staticmethod
    def add_upload_data(file, table_name, namespace, head=1, partition=16,
                        id_delimiter=",", extend_sid = False, auto_increasing_sid = False):
        data_conf = {"file": file,
                     "table_name": table_name,
                     "namespace": namespace,
                     "head": head,
                     "partition": partition,
                     "id_delimiter": id_delimiter,
                     "extend_sid": extend_sid,
                     "auto_increasing_sid": auto_increasing_sid}
        return data_conf
    
    # def callback_metric(self, metric_name, metric_namespace, metric_data):
    #     self.tracker.log_metric_data(metric_name=metric_name,
    #                                  metric_namespace=metric_namespace,
    #                                  metrics=metric_data)
    #     self.tracker.set_metric_meta(metric_namespace,
    #                                  metric_name,
    #                                  MetricMeta(name='upload',
    #                                             metric_type='UPLOAD'))
    
    def prevent_repeat_upload(self, table_name, namespace):
        data_table = self.session.get_table(table_name, namespace)
        if not data_table:
            print("{}".format("Not Repeat"))
        else:
            data_table.destroy()
            #self.session.delete_data_table_meta(table_name, namespace)
            # self.session.cleanup(table_name, namespace)
            # self.session.cleanup(table_name + ".meta", namespace)
            print("{}".format("Clean the Repeat Data"))
            data_table = self.session.get_table(table_name, namespace)
            print(data_table)


if __name__ == '__main__':
    upload = Upload()
    fileinfo = Upload.add_upload_data("python/worker2/test/iris_11.csv", "yyf6_data", "breast_vert_provider", 1, 1)
    param = {"fileinfo": fileinfo}
    upload.set_taskid("1234")
    upload.run(param)
