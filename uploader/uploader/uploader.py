from typing import List, Tuple
import requests
import os
import enum
from datetime import datetime
import dataclasses

API_URL = os.environ.get("DB_UPLOADER_URL", "http://avocado.enerzai.com:5001")

class DeviceFarm(enum.Flag):
    AVOCADO = enum.auto()
    BLUEBERYY = enum.auto()
    CARROT = enum.auto()
    DURIAN = enum.auto()
    EGGPLANT = enum.auto()
    FIG = enum.auto()
    GUAVA = enum.auto()
    HAZELNUT = enum.auto()
    ICEMANGO = enum.auto()
    JUJUBE = enum.auto()
    LIME = enum.auto()
    MANDARIN = enum.auto()
    NUTMEG = enum.auto()
    OLIVE = enum.auto()
    PINEAPPLE = enum.auto()

def check_response(resp: requests.Response):
    if resp.status_code != 200:
        res = resp.json()
        raise RuntimeError("DB backend threw an error : ", {res['message']})

def post(data, postfix):
    resp = requests.post(f"{API_URL}/{postfix}", json=data)
    check_response(resp)

def get(data, postfix):
    resp = requests.get(f"{API_URL}/{postfix}", json=data)
    check_response(resp)
    return resp.json()

class GroupLoader:
    def set_group(self, device : DeviceFarm, latency : float, date : datetime):
        data = {'device' : device.value,
                'latency': latency,
                'date': date.timestamp()}
        return get({'data': data}, 'group/set_group')
    def get_groups(self):
        return get({}, 'group')

@dataclasses.dataclass
class ModelLoader():
    modelname : str
    framework : str
    input_shape : List[Tuple]
    device : DeviceFarm
    commit : str
    groupid : str
    
    def __post_init__(self):
        self.modeldata = {'modelname': self.modelname,
                'input_shape': self.input_shape,
                'framework': self.framework,
                'device': self.device.value,
                'commit' : self.commit,
                'groupid': self.groupid}
    def upload_model(self, date : datetime, latency : float):
        data = {'latency' : latency,
                'date': date.timestamp()}
        data.update(self.modeldata)
        post({'data':  data}, 'model/upload_model')
    
    def get_latency(self):
        return get({'data': self.modeldata}, '/model/get_latency')
    
    def get_all_result(self):
        data = self.modeldata.copy()
        data.pop('commit')
        return get({'data': data}, 'model/get_all_result')
    
@dataclasses.dataclass
class LayerLoader():
    attr : dict
    input_shape : List[Tuple]
    opcode : str
    device : DeviceFarm
    commit : str
    commitdate : datetime
    groupid : str
    
    def __post_init__(self):
        self.opdata = {'attr': self.attr,
                'input_shape': self.input_shape,
                'opcode': self.opcode,
                'device': self.device.value,
                'commit' : self.commit,
                'groupid': self.groupid,
                'commitdate': self.commitdate.timestamp()}
    
    def get_commits(self):
        return get({'data': self.opdata}, 'layer/get_commits')
    
    def upload_layer(self, optim_param, latency, date):
        data = {'optim_param' : optim_param,
                'latency': latency,
                'date' : date.timestamp()}
        data.update(self.opdata)
        post({'data': data}, 'layer/layerupload')
    
    def get_group(self):
        return get({'data': self.opdata}, 'layer/get_group')
    
    def set_optim(self):
        post({'data': self.opdata}, 'layer/set_optim')
        
    def get_optim(self):
        return get({'data': self.opdata}, 'layer/get_optim')
    
    def get_all_optim(self):
        return get({'data': self.opdata}, 'layer/get_all_optim')
    
    def get_profiles(self):
        return get({'data': self.opdata}, 'layer/get_profiles')
    
    def initialize_latency(self, optim_param):
        data = {'optim_param': optim_param}
        data.update(self.opdata)
        post({'data': data}, 'layer/initialize_latency')
        
