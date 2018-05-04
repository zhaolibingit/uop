# -*- coding: utf-8 -*-
import os

APP_ENV = "development"
basedir = os.path.abspath(os.path.dirname(__file__))

DEV_CRP_URL = "http://172.28.32.32:8001/"
TEST_CRP_URL = "http://172.28.32.32:8001/"
PROD_CRP_URL = "http://172.28.32.32:8001/"



class BaseConfig:
    DEBUG = False

class DevelopmentConfig(BaseConfig):
    TESTING = True
    DEBUG = True
    MONGODB_SETTINGS = {
            'db': 'uop',
            'host': '172.28.20.124',
            'port': 27017,
            'username': 'uop',
            'password': 'uop',
            }
    CRP_URL = {
        'dev': DEV_CRP_URL,
        'test': TEST_CRP_URL,
        'prod': PROD_CRP_URL,
    }
    #CMDB_URL = "http://cmdb-dev.syswin.com/"
    CMDB_URL = "http://172.28.20.124:6000/" #如果是None 不走cmdb1,0
    CMDB2_URL = "http://cmdb2-test.syswin.com/"
    host_instance_id = "2a4d89e3e48b471da0ea41c1"
    CMDB2_OPEN_USER = "uop"

    # CMDB知识库变动时，需要改动，或添加
    CMDB2_ENTITY = {
        "Person": "d8098981df71428784e65427",
        "department": "9a544097f789495e8ee4f5eb",
        "yewu": "c73339db70cc4647b515eaca",
        "Module": "9e97b54a4a54472e9e913d4e",
        "project": "59c0af57133442e7b34654a3",
        "host": "b593293378c74ba6827847d3",
        "container": "d0f338299fa34ce2bf5dd873",
        "virtual_device": "d4ad23e58f31497ca3ad2bab",
        "tomcat": "d1b11a713e8842b2b93fe397",
        "mysql": "e5024d360b924e0c8de3c6a8",
        "redis": "de90d618f7504723b677f196",
        "mongodb": "9bc4a41eb6364022b2f2c093",
        "nginx": "3671f248bdc74d2fb6aa590c",
    }
    UOPCODE_CMDB2 = {
        "c73339db70cc4647b515eaca": "business",
        "9e97b54a4a54472e9e913d4e": "module",
        "59c0af57133442e7b34654a3": "project"
    }
    # CMDB知识库变动时，改动此字典与 CMDB2_ENTITY 保持一致即可，为确保查询性能，稍有冗余，但同一起点的实体id只能有一个视图
    CMDB2_VIEWS = {
        # 注意：定时任务只会缓存1，2，3 三个视图下的基础模型数据
        "1": ("B7", u"工程 --> 物理机，用于拿到各层间实体关系信息", "59c0af57133442e7b34654a3"),     # （视图名，描述，起点实体id）
        "2": ("B6", u"部门 --> 资源，用于分级展示业务模块工程", "9a544097f789495e8ee4f5eb"),
        "3": ("B5", u"人 --> 部门 --> 工程", "d8098981df71428784e65427"),


        "4": ("B8", u"tomcat --> 机房，展示tomcat资源视图", "d1b11a713e8842b2b93fe397"),
        "5": ("B9", u"mysql --> 机房，展示mysql资源视图", "e5024d360b924e0c8de3c6a8"),
        "6": ("B10", u"mongodb--> 机房，展示mongodb资源视图", "9bc4a41eb6364022b2f2c093"),
        "7": ("B11", u"redis --> 机房，展示redis资源视图", "de90d618f7504723b677f196"),
        "8": ("B12", u"物理机信息", "b593293378c74ba6827847d3"),
        "9": ("B13", u"模块 --> 物理机，用于拿到各层间实体关系信息", "9e97b54a4a54472e9e913d4e"),
        "10": ("B14", u"nginx --> 机房，展示nginx资源视图", "3671f248bdc74d2fb6aa590c")
        # "5": ("B3", u"资源 --> 机房"),
    }

    UPLOAD_FOLDER = "/data/"
    BASE_K8S_IMAGE = "reg1.syswin.com/base/uop-base-k8s:v-1.0.1"
    K8S_NGINX_PORT = "80"
    K8S_NGINX_IPS = ["172.28.13.5"]
configs = {
    'development': DevelopmentConfig,
}
