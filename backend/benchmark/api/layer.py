from models.device import DeviceFarm
from models.layer import LayerDB, Profile
from models.layer import LayerDB, Profile, get_or_create_layer
import random
from flask import jsonify, Blueprint
import datetime

bp = Blueprint("layer", __name__, url_prefix="/layer")

@bp.route('/profiles')
def get_all_profiles():
    profiles = Profile.objects()
    return jsonify(profiles), 200

@bp.route('/layerupload')
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

@bp.route('/get_group')
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

@bp.route('/set_optim')
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

@bp.route('/get_optim')
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

@bp.route('/set_group')
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