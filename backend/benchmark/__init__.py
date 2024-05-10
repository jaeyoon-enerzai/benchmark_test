from flask import Flask, jsonify
from flask_mongoengine import MongoEngine
from mongoengine import connect
from models.layer import LayerDB, Profile
from models.device import DeviceFarm
from models.utils import get_or_create_layer
from typing import Dict
from werkzeug.exceptions import BadRequest
import sys
import random
import datetime

app = Flask(__name__)

app.config['MONGODB_SETTINGS'] = {
    'db': 'benchmark',
    'host': 'db',
    'port': 27017
}
MONGODB_URL = "mongodb://localhost/benchmark"
db = MongoEngine()
db.init_app(app)

# @app.route('/modelupload')
# def upload_model():
#     model = ModelDB(modelname="mobilenet")
#     device = DeviceFarm.AVOCADO
#     model.device = device
#     model.commit = "abcdef"
    
#     repeatnum = random.randint(1,5)
#     modelstat = ModelStat()
#     for _ in range(repeatnum):
#         date = datetime.datetime.now()
#         latency = random.random()
#         modelrun_onetime = DateLatency(date=date, latency=latency)
#         modelstat.datelatency.append(modelrun_onetime)
#     model.latency = modelstat
    
#     for baseline in ['tf', 'openvino', 'torch']:
#         if random.random() > 0.5:
#             repeatnum = random.randint(1,5)
#             modelstat = ModelStat()
#             for _ in range(repeatnum):
#                 date = datetime.datetime.now()
#                 latency = random.random()
#                 modelrun_onetime = DateLatency(date=date, latency=latency)
#                 modelstat.datelatency.append(modelrun_onetime)
#             model.baseline_latency[baseline] = modelstat
#     model.save()
#     return jsonify(model), 200

@app.route('/profiles')
def get_all_profiles():
    profiles = Profile.objects()
    return jsonify(profiles), 200

@app.route('/layerupload')
def upload_layer():
    # TODO - change by parsing args input
    ker = 3
    attr = {'kernel_size': (ker, ker), 'stride': (1,1), 'padding': (0,0,0,0)}
    device = DeviceFarm.LIME
    input_shape = [(1,2,3,4)]
    opcode = 'Conv2D'
    commit = 'abcdef'
    
    print("Any LAYER EXISTS?")
    all_layers = LayerDB.objects()
    print(all_layers)
    
    layer = get_or_create_layer(opcode, attr, input_shape, device, commit, datetime.datetime.now())
    
    # optim_param = {'unroll' : list(random.randint(1,2) for _ in range(3)), 
    #                'vector' : list(random.randint(1,2) for _ in range(3))}
    optim_param = {'unroll': (2, 2, 1),
                   'vector': (1, 2, 2)}
    latency = random.random()
    date = datetime.datetime.now()
    
    layer.upload_latency("1", optim_param, date, latency)
    
    print(LayerDB.objects())
    
    return jsonify(layer), 200

@app.route('/get_group')
def get_group():
    # TODO - change by parsing args input
    ker = 3
    attr = {'kernel_size': (ker, ker), 'stride': (1,1), 'padding': (0,0,0,0)}
    device = DeviceFarm.LIME
    input_shape = [(1,2,3,4)]
    opcode = 'Conv2D'
    commit = 'abcdef'
    
    layer = get_or_create_layer(opcode, attr, input_shape, device, commit, datetime.datetime.now())
    
    return jsonify(layer.get_group_represent()), 200

@app.route('/set_optim')
def set_optim():
    # TODO - change by parsing args input
    ker = 3
    attr = {'kernel_size': (ker, ker), 'stride': (1,1), 'padding': (0,0,0,0)}
    device = DeviceFarm.LIME
    input_shape = [(1,2,3,4)]
    opcode = 'Conv2D'
    commit = 'abcdef'
    
    layer = get_or_create_layer(opcode, attr, input_shape, device, commit, datetime.datetime.now())
    
    layer.set_best_optim()
    
    return {}

@app.route('/get_optim')
def get_optim():
    # TODO - change by parsing args input
    ker = 3
    attr = {'kernel_size': (ker, ker), 'stride': (1,1), 'padding': (0,0,0,0)}
    device = DeviceFarm.LIME
    input_shape = [(1,2,3,4)]
    opcode = 'Conv2D'
    commit = 'abcdef'
    
    layer = get_or_create_layer(opcode, attr, input_shape, device, commit, datetime.datetime.now())
    
    return jsonify(layer.get_best_optim()), 200

@app.route('/set_group')
def set_group():
    # TODO - change by parsing args input
    ker = 3
    attr = {'kernel_size': (ker, ker), 'stride': (1,1), 'padding': (0,0,0,0)}
    device = DeviceFarm.LIME
    input_shape = [(1,2,3,4)]
    opcode = 'Conv2D'
    commit = 'abcdef'
    
    layer = get_or_create_layer(opcode, attr, input_shape, device, commit, datetime.datetime.now())
    
    newgrp = layer.set_group()
    return newgrp
    
""" @app.route('/result', methods=['POST'])
def upload_layer():
    data = request.json.get('data')
    
    if data is None:
        raise BadRequest("omitted required data")
 """    
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)