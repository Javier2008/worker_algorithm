#
#  Created by yuyunfu
#   2022/10/8 
#

from pyspark import SparkContext, SparkConf

from common.common import conf_utils


def get_spark_conf():
    spark_conf = conf_utils.get_base_config("spark")
    if spark_conf:
        spark_conf = spark_conf.get("spark")
    
    if not spark_conf:
        raise Exception("Spark configure don't exist")
    
    conf = SparkConf().setAppName("PythonWork").setMaster(spark_conf.get("url"))
    return conf


def operation_add(x, y):
    return x + y


if __name__ == '__main__':
    sc = SparkContext()
    r = sc.textFile("/home/tsingj_ubuntu/yuyunfu/pythonwork/python_code/worker2/test/data/iris_22.csv")
    r = r.flatMap(lambda line: line.split(",")).map(lambda x: (x, 1))
    r2 = r.reduceByKey(operation_add).collect()
    
    print(r2)
    print("finish")
