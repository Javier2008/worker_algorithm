from algorithm.feature.upload.upload import Upload

def upload_guest_table():
    upload = Upload()
    fileinfo = Upload.add_upload_data("/Users/yuyunfu/Downloads/iris_11.csv", "yyf4_data", "breast_vert_promoter", 1, 1)
    param = {"fileinfo": fileinfo}
    upload.set_taskid("1234")
    upload.run(param)
    
def upload_host_table():
    upload = Upload()
    fileinfo = Upload.add_upload_data("/Users/yuyunfu/Downloads/iris_22.csv", "yyf5_data", "breast_vert_provider", 1, 1)
    param = {"fileinfo": fileinfo}
    upload.set_taskid("1234")
    upload.run(param)
    
if __name__ == '__main__':
    upload_host_table()