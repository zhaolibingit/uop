# -*- coding: utf-8 -*-
'''
 Logic Layer
'''
import json
import requests
import sys
import os
from uop.log import Log
from uop.util import TimeToolkit, response_data
from config import configs, APP_ENV
from datetime import datetime
from flask import jsonify

curdir = os.path.dirname(os.path.abspath(__file__))
__all__ = [
    "get_uid_token", "Aquery", "get_entity",
    "subgrath_data", "package_data", "get_entity_from_file"
]
CMDB2_URL = configs[APP_ENV].CMDB2_URL
CMDB2_MODULE ={
    0: "Person",
    1: "department", #部门
    3: "Moudle", #模块
    2: "yewu", #业务
    4: "project", #工程
}

id_property = {
    2: [
        {
            "id": 1,
            "name": u"名称",
            "code": "name",
            "value_type": "str"
        },
        {
            "id": 2,
            "name": u"英文名称",
            "code": "e-name",
            "value_type": "str"
        },
    ],
    3: [
        {
            "id": 1,
            "name": u"名称",
            "code": "name",
            "value_type": "str"
        },
        {
            "id": 2,
            "name": u"英文名称",
            "code": "e-name",
            "value_type": "str"
        },
    ],
    4: [
        {
            "id": 1,
            "name": u"名称",
            "code": "name",
            "value_type": "str"
        },
        {
            "id": 2,
            "name": u"英文名称",
            "code": "e-name",
            "value_type": "str"
        },
    ],
    5: [
        {
            "id": 1,
            "name": u"名称",
            "code": "name",
            "value_type": "str"
        },
        {
            "id": 2,
            "name": u"英文名称",
            "code": "e-name",
            "value_type": "str"
        },
    ],
}


#临时从本地文件读取数据
def get_data_from_file(td):
    '''
    临时从文本里获取数据
    :param td:
    :return:
    '''
    with open(curdir + "/json.txt", "rb") as fp:
        whole_data = json.load(fp)["data"]
    instance_id = td["data"]["instance"]["instance_id"]
    model_id = int(td["data"]["instance"]["model_id"])
    # Log.logger.info("whole_data:{},{}\n, instance_id:{}".format(whole_data, type(whole_data), instance_id))
    data = [wd for wd in whole_data if str(wd["parent_id"]) == str(instance_id)]
    data = data[0] if data else {"instance": [], "model_id": model_id + 1} #假数据中只需+1
    data.update(property=id_property[int(model_id + 1)])
    return data


#临时将数据写入本地文件
def push_data_to_file(parent_id, model_id, property):
    '''
    向文本里写数据
    :param property:
    [
    {   "name" : "实例中文名",
        ""
    }
    ]
    :return:
    '''
    try:
        with open(curdir + "/json.txt", "rb") as fp:
            whole_data = json.load(fp)["data"]
        Log.logger.info("whole_data:{}\nparent_id:{}\nproperty:{},{}".format(whole_data, parent_id, property, type(property)))
        data = [p for p in property if str(p["code"]) == "name"][0]
        node = [wd for wd in whole_data if str(wd["parent_id"]) == str(parent_id)]
        if node:
            node = node[0]
            node_id_list = [int(n["instance_id"]) for n in node["instance"]]
            new_id = str(max(node_id_list) + 1)
        else:
            node = {
                "parent_id": int(parent_id),
                "model_id": int(model_id),
                "instance":[],
            }
            new_id = str(model_id) + '1'
        new_instance = {
            "name": data["value"],
            "instance_id": new_id
        }
        node["instance"].append(new_instance)
        for k, v in enumerate(whole_data):
            if str(v["parent_id"]) == str(parent_id):
                whole_data[k] = node
                break
        else:
            whole_data.append(node)
        Log.logger.info("node:{},type:{}".format(node, type(node)))
        Log.logger.info("new whole_data: {}".format(whole_data))
        with open(curdir + "/json.txt", "w") as fp:
            json.dump({"data": whole_data}, fp)
    except Exception as exc:
        Log.logger.error("push_data_to_file: {}".format(str(exc)))
    return node


# 获取uid，token
def get_uid_token(username="admin", password="admin", sign=""):
    uid, token = 0, 0
    url = CMDB2_URL + "cmdb/openapi/login/"
    data = {
        "username": username,
        "password": password,
        "sign": sign,
        "timestamp": TimeToolkit.local2utctimestamp(datetime.now())
    }
    data_str = json.dumps(data)
    try:
        ret = requests.post(url, data=data_str)
        Log.logger.info(ret.json())
        uid, token = ret.json()["data"]["uid"], ret.json()["data"]["token"]
    except Exception as exc:
        Log.logger.error("get uid from CMDB2.0 error:{}".format(str(exc)))
    return uid, token


# 将实体信息数据导入文件
def push_entity_to_file(data):
    entity_list = []
    try:
        for d in data:
            for dc in d.get("children", []):
                entity_list.append({
                    "code": dc.get("code",""),
                    "name": dc.get("name",""),
                    "id": dc.get("id",""),
                    "property": dc.get("parameters",[])
                })
        with open(curdir + "/.entity.txt", "w") as fp:
            json.dump({"entity": entity_list}, fp)
    except Exception as exc:
        Log.logger.error("push_entity_to_file error:{} ".format(str(exc)))
    return entity_list


def get_entity_from_file(filters):
    assert(isinstance(filters, dict))
    if not os.path.exists(curdir + "/.entity.txt"):
        whole_entity = get_entity()
    else:
        with open(curdir + "/.entity.txt", "rb") as fp:
            whole_entity = json.load(fp)["entity"]
    compare_entity = map(lambda  x:{'id': x["id"], "name": x["name"], "code": x["code"], "property": str(x["property"])}, whole_entity)
    single_entity = filter(lambda x:set(x.values()) & set(filters.values()), compare_entity)
    if single_entity:
        se = map(lambda x:{'id': x["id"], "name": x["name"], "code": x["code"], "property": str(x["property"])}, single_entity)


    return single_entity


#A类视图查询
def Aquery(args):
    '''
    A 类视图 查询
    :param data:
    :return:
    '''
    view_dict = {
        "B5": "405cf4f20d304da3945709d3",  # 人 --> 部门 --> 工程 405cf4f20d304da3945709d3
        "B4": "29930f94bf0844c6a0e060bd",  # 资源 --> 环境 --> 机房
        "B3": "e7a8ed688f2e4c19a3aa3a65",  # 资源 --> 机房
        "B2": "",
        "B1": "",
    }
    name, code, uid, token, instance_id, model_id, self_model_id = \
        args.name, args.code, args.uid, args.token, args.instance_id, args.model_id, args.self_model_id
    url_action = CMDB2_URL + "cmdb/openapi/scene_graph/action/"
    url_instance = CMDB2_URL + "cmdb/openapi/query/instance/"  # 如果传instance_id，调用这个直接拿到下一层数据
    if not uid or not token:
        uid, token = get_uid_token()
    data_action = {
        "uid": uid,
        "token": token,
        "sign": "",
        "data": {
            "id": view_dict["B5"],
            "name": "",
            "entity": [{
                "id": "",  # 实体id
                "parameters": [{
                    "code": code,  # 属性code
                    "value": name  # 属性值，必须具备唯一性， 如工号
                }]
            }]
        }
    }
    data_instance = {
        "uid": uid,
        "token": token,
        "sign": "",
        "data": {
            "instance": {
                "model_id": self_model_id ,
                "instance_id": instance_id
            }
        }
    }
    data_action_str = json.dumps(data_action)
    data_instance_str = json.dumps(data_instance)
    try:
        if instance_id:
            Log.logger.info("url_instance request data:{}".format(data_instance))
            ret = requests.post(url_instance, data=data_instance_str)
            Log.logger.info("url_instance return:{}".format(ret.json()))
            data = ret.json()["data"]["instance"]
            data = filter(lambda x:x["entity_id"] == model_id, data)
            data = analyze_data(data, model_id)
            result = response_data(200, "success", data.update({"uid": uid, "token": token}))
        else:
            Log.logger.info("url_action request data:{}".format(data_action))
            ret = requests.post(url_action, data=data_action_str)
            # Log.logger.info("url_action return:{}".format(ret.json()))
            data = analyze_data(ret.json()["data"]["instance"], model_id)
            result = response_data(200, "success", data.update({"uid": uid, "token": token}))
    except Exception as exc:
        Log.logger.error("Aquery error:{}".format(str(exc)))
        result = response_data(200, str(exc), "")
    return result


#从B类视图中解析出A类数据
def analyze_data(data, entity_id=None):
    ret = {
        "instance":[]
    }
    if entity_id:
        data = filter(lambda x: x.get("entity_id") == entity_id, data)
    instance = map(lambda x: {"instance_id": x.get("instance_id"), "name": x.get("name")}, data)
    ret["instance"] = instance
    return ret


#获取所有模型实体的id及属性信息存到文件
def get_entity():
    '''
    [
    {
        "id": 实体id
        "name": 实体名
        "code": 实体英文名
        "parameters":[
            {
                'id': 属性id
                'name': 属性名
                'code': 属性编码
                'value_type': 属性类型
            }
        ]
    }
    ]
    :param req_data:
    :return:
    '''
    url = CMDB2_URL + "cmdb/openapi/entity/group/"
    uid, token = get_uid_token()
    req_data = {
        "uid": uid,
        "token": token,
        "sign": "",
        "data": {
            "name":"",
            "code":"",
            "id":""
        }
    }
    data_str = json.dumps(req_data)
    entity_info = {}
    try:
        ret = requests.post(url, data=data_str).json()
        if ret["code"] != 0:
            req_data["uid"], req_data["code"] = get_uid_token()
            data_str = json.dumps(req_data)
            ret = requests.post(url, data=data_str).json()
        # Log.logger.info("get entity info from CMDB2.0: {}".format(ret))
        entity_info = push_entity_to_file(ret.get("data"))
    except Exception as exc:
        Log.logger.error("get entity info from CMDB2.0 error: {}".format(exc))
    return entity_info


#插入子图
def subgrath_data(args):
    '''
    插入子图数据，并返回图结果
    :param args:
    :return:
    '''
    entity_id, instance_id, property, uid, token = \
        args.model_id, args.instance_id, args.property, args.uid, args.token
    if not uid or not token:
        uid, token = get_uid_token()
    url = CMDB2_URL + "cmdb/openapi/graph/"
    format_data, graph_data = {}, {}
    data = {
        "uid": uid,
        "token": token,
        "sign": "",
        "data": {
            "instance": [
                {
                    "entity_id": entity_id,
                    "instance_id": "",
                    "parameters":[
                        {}
                    ]
                }
            ],
            "relation": []
        }
    }
    data_str = json.dumps(data)
    try:
        # ret = requests.post(url, data=data_str).json()
        graph_data=push_data_to_file(instance_id, entity_id, property)
        format_data = package_data(graph_data, data)
    except Exception as exc:
        Log.logger.error("graph_data: {}".format(graph_data))
    return format_data


#组装业务工程模块接口数据
def package_data(ret, ut):
    '''
    传给前端的数据格式
    "uid": 1,
    "token": wtf,
    "module_id":123, #实体id
    "instance":[
        {
        "name":u"toon基础",
        "instance_id":123-1 #实例id
        },
        {
        "name":u"企通",
        "instance_id":123-2
        },
    ],
    ]
    '''
    # data = {
    #     "uid": 1,
    #     "token": 'wtf',
    #     "parent_id":2,
    #     "entity_id":3, #实体id
    #     "instance":[
    #         {
    #             "name":u"toon基础",
    #             "instance_id":'1231' #实例id
    #         },
    #         {
    #             "name":u"企通",
    #             "instance_id":'1232'
    #         },
    #         {
    #             "name": u"政通",
    #             "instance_id": '1233'
    #         },
    #         {
    #             "name": u"食尚",
    #             "instance_id": '1234'
    #         },
    #     ],
    # }
    ret.update(ut)
    ret.pop("data")
    return ret
