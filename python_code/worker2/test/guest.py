#
#  Created by yuyunfu
#   2022/9/15 
#
import json


from common.common import log
from common.common.file_utils import get_project_base_directory
log.setDirectory(get_project_base_directory("log/guest"))

from algorithm.feature.upload.upload import Upload
from common.metastore.db_models import init_database_tables
from worker2.task_executor import TaskExecutor

model_id = "1234567882"
job_conf = {
    "job_type": "train",
    "initiator": {
        "role": "guest",
        "party_id": 9999
    },
    "role": {
        "arbiter": [
            8888
        ],
        "host": [
            8888
        ],
        "guest": [
            9999
        ]
    },
    "local": {
        "role": "guest",
        "party_id": 9999
    },
}
task_conf = {
    "inheritance_info": {},
    "computing": "STANDALONE",
    "federation": "STANDALONE",
    "storage": "STANDALONE",
    "engines_address": {
        "computing": {
            "cores_per_node": 2,
            "nodes": 1
        },
        "federation": {
            "cores_per_node": 20,
            "nodes": 1,
            "host": "192.168.200.88",
            "port": "26650",
            "mng_port": "28080",
            "cluster": "standalone",
            # all parties should use a same tenant
            "tenant": "tenant26",
            # message ttl in minutes
            "topic_ttl": 5
        },
        "storage": {
            "cores_per_node": 20,
            "nodes": 1
        }
    },
    "federated_mode": "SINGLE",
    "task_cores": 1,
    "computing_partitions": 1,
    "adaptation_parameters": {
        "task_nodes": 1,
        "task_cores_per_node": 1,
        "task_memory_per_node": 0,
        "request_task_cores": 1,
        "if_initiator_baseline": False
    },
    "src_user": None
}

task_param_reader = {
    "module": "Reader",
    "CodePath": "reader",
    "model_id": "arbiter-10000#guest-9999#host-10000#model",
    "model_version": model_id,
    "input": {
        "data": {
        }
    },
    "output": {
        "data": [
            "data"
        ]
    },
    "param": {
        "table": {
            "name": "X_9999_42",
            "namespace": "test_data"
        },
        "_name": "Reader#reader_0"
    }
}

task_param_dataio = {
    "module": "DataIO",
    "CodePath": "DataIO",
    "model_id": "arbiter-10000#guest-9999#host-10000#model",
    "model_version": model_id,
    "input": {
        "data": {
            "data": [
                "reader_0.data"
            ]
        }
    },
    "output": {
        "data": [
            "data"
        ],
        "model": [
            "model"
        ]
    },
    "param": {
        "missing_fill": True,
        "missing_fill_method": "mean",
        "outlier_replace": False,
        "outlier_replace_method": "designated",
        "outlier_impute": "-9999",
        "outlier_replace_value": 0.66,
        "with_label": True,
        "label_name": "y",
        "label_type": "int",
        "output_format": "dense"
    }
}

task_param_intersection = {
    "module": "intersection",
    "CodePath": "intersection",
    "model_id": "arbiter-10000#guest-9999#host-10000#model",
    "model_version": model_id,
    "input": {
        "data": {
            "data": [
                "dataio_0.data"
            ]
        }
    },
    "output": {
        "data": [
            "data"
        ],
        "cache": [
            "cache"
        ]
    },
    "param": {
        "intersect_method": "dh"
    }
}
task_param_hetero_feature_binning = {
    "module": "hetero_feature_binning",
    "CodePath": "hetero_feature_binning",
    "model_id": "arbiter-10000#guest-9999#host-10000#model",
    "model_version": model_id,
    "input": {
        "data": {
            "data": [
                "intersection_0.data"
            ]
        }
    },
    "output": {
        "data": [
            "data"
        ],
        "model": [
            "model"
        ]
    },
    "param": {
        "method": "optimal",
        "bin_indexes": -1,
        "optimal_binning_param": {
            "metric_method": "iv",
            "init_bucket_method": "quantile"
        }
    }
}

task_param_statistics = {
    "module": "statistic",
    "CodePath": "statistic",
    "model_id": "arbiter-10000#guest-9999#host-10000#model",
    "model_version": model_id,
    "input": {
        "data": {
            "data": [
                "intersection_0.data"
            ]
        }
    },
    "output": {
        "model": [
            "model"
        ]
    },
    "param": {
        
    }
}

task_param_hetero_feature_selection = {
    "module": "hetero_feature_selection",
    "CodePath": "hetero_feature_selection",
    "model_id": "arbiter-10000#guest-9999#host-10000#model",
    "model_version": model_id,
    "input": {
        "data": {
            "data": [
                "intersection_0.data"
            ]
        },
        "isometric_model": [
            "hetero_feature_binning_0.model",
            "statistics_0.model"
        ]
    },
    "output": {
        "data": [
            "data"
        ],
        "model": [
            "model"
        ]
    },
    "param": {
        "select_col_indexes": -1,
        "filter_methods": [
            "unique_value",
            "iv_filter",
            "statistic_filter"
        ],
        "unique_param": {
            "eps": 1e-06
        },
        "iv_param": {
            "metrics": [
                "iv",
                "iv"
            ],
            "filter_type": [
                "top_k",
                "threshold"
            ],
            "take_high": [
                True,
                True
            ],
            "threshold": [
                10,
                0.1
            ]
        },
        "statistic_param": {
            "metrics": [
                "coefficient_of_variance",
                "skewness"
            ],
            "filter_type": [
                "threshold",
                "threshold"
            ],
            "take_high": [
                True,
                False
            ],
            "threshold": [
                0.001,
                -0.01
            ]
        }
    }
}

task_param_feature_scale = {
    "module": "feature_scale",
    "CodePath": "feature_scale",
    "model_id": "arbiter-10000#guest-9999#host-10000#model",
    "model_version": model_id,
    "input": {
        "data": {
            "data": [
                "hetero_feature_selection_0.data"
            ]
        }
    },
    "output": {
        "data": [
            "data"
        ],
        "model": [
            "model"
        ]
    },
    "param": {
        "method": "standard_scale"
    }
}

task_param_linear_model = {
    "module": "linear_model",
    "CodePath": "linear_model",
    "model_id": "arbiter-10000#guest-9999#host-10000#model",
    "model_version": model_id,
    "input": {
        "data": {
            "train_data": [
                "feature_scale_0.data"
            ],
            # "validate_data": [
            #    "feature_scale_1.data"
            # ]
        }
    },
    "output": {
        "data": [
            "data"
        ],
        "model": [
            "model"
        ]
    },
    "param": {
        "penalty": "L2",
        "tol": 0.0001,
        "alpha": 0.01,
        "optimizer": "nesterov_momentum_sgd",
        "batch_size": -1,
        "learning_rate": 0.15,
        "init_param": {
            "init_method": "zeros"
        },
        "max_iter": 5,
        "early_stop": "diff",
        "validation_freqs": None,
        "early_stopping_rounds": None
    }
}


def exec_feature(jobid, taskversion, feature):
    arg = {
        "job_id": jobid,
        "task_id": f"{jobid}_{feature}_0",
        "component_name": f"{feature}_0",
        "task_version": taskversion,
        "role": "guest",
        "party_id": 9999,
        "run_ip": "127.0.0.1",
        "federation_session_id": "session",
        "task_conf": json.dumps(task_conf),
        "task_param": "",
        "job_conf": json.dumps(job_conf),
        "user": "Javier"
    }
    
    model = __import__("__main__")
    param_fun = getattr(model, f"task_param_{feature}")
    arg["task_param"] = json.dumps(param_fun)
    
    t = TaskExecutor()
    t.run(**arg)


if __name__ == '__main__':
    init_database_tables()
    
    job_id = "1234567812"
    task_version = "1"

    upload = Upload()
    fileinfo = Upload.add_upload_data("python_code/worker2/test/data/X_10000_42.csv", "X_9999_42", "test_data", 1, 2)
    param = {"fileinfo": fileinfo, "id_index": 1}
    upload.set_taskid("1234")
    upload.run(param)

    
    # dataio
    log.getLogger().info("safasfasfa")
    print("start reader")
    #exec_feature(job_id, task_version, "reader")
    # print("start dataio")
    #exec_feature(job_id, task_version, "dataio")
    #print("start intersection")
    #exec_feature(job_id, task_version, "intersection")
    
    ##一次只能跑一个，否则pulsar的通讯会异常
    
    #exec_feature(job_id, task_version, "hetero_feature_binning")
    #exec_feature(job_id, task_version, "statistics")
    #exec_feature(job_id, task_version, "hetero_feature_selection")
    #exec_feature(job_id, task_version, "feature_scale")
    #exec_feature(job_id, task_version, "linear_model")
    print("!!!!!!finish process!!!!!!!!!!!!")

