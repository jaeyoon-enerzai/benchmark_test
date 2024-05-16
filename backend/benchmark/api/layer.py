from models.device import DeviceFarm
from models.layer import LayerDB, Profile
from models.layer import LayerDB, Profile, get_or_create_layer, get_layers
import random
from flask import jsonify, Blueprint, request
import datetime

bp = Blueprint("layer", __name__, url_prefix="/layer")

@bp.route('/profiles')
def get_all_profiles():
    profiles = Profile.objects()
    return jsonify(profiles), 200

@bp.route('/')
def get_all_layer():
    layers = LayerDB.objects()
    return jsonify(layers), 200

def _common_info(data: dict):
    attr = data['attr']
    device = data['device']
    input_shape = data['input_shape']
    opcode = data['opcode']
    commit = data['commit']
    groupid = data['groupid']
    commitdate = datetime.datetime.fromtimestamp(data['commitdate'])
    return attr, device, input_shape, opcode, commit, groupid, commitdate

@bp.route('/get_commits')
def get_commits():
    attr, device, input_shape, opcode, commit, groupid, commitdate = _common_info(request.json.get('data'))
    layers = get_layers(opcode, attr, input_shape, device)
    commits = list(set([(l_.commit, l_.commitdate) for l_ in layers])) # do not consider group
    commits = sorted(commits, key=lambda t: t[1])[::-1]
    return jsonify({'commits': commits}), 200

@bp.route('/layerupload', methods=('POST',))
def upload_layer():
    data = request.json.get('data')
    attr, device, input_shape, opcode, commit, groupid, commitdate = _common_info(data)
    optim_param = data['optim_param']
    latency = data['latency']
    date = datetime.datetime.fromtimestamp(data['date'])

    layer = get_or_create_layer(opcode, attr, input_shape, device, commit, commitdate)
    
    layer.upload_latency(groupid, optim_param, date, latency)
        
    return jsonify(layer), 200

@bp.route('/get_group')
def get_group():
    attr, device, input_shape, opcode, commit, groupid, commitdate = _common_info(request.json.get('data'))
    
    layer = get_or_create_layer(opcode, attr, input_shape, device, commit, commitdate)
    
    return jsonify(layer.get_group_represent()), 200

@bp.route('/set_optim', methods=('POST',))
def set_optim():
    attr, device, input_shape, opcode, commit, groupid, commitdate = _common_info(request.json.get('data'))
   
    layer = get_or_create_layer(opcode, attr, input_shape, device, commit, commitdate)
    
    layer.set_best_optim()
    
    return {}

@bp.route('/get_optim')
def get_optim():
    """return the best optim across all groups

    Returns:
        Dict: dictionary for optim param
        int: response code
    """
    attr, device, input_shape, opcode, commit, groupid, commitdate = _common_info(request.json.get('data'))
    
    layer = get_or_create_layer(opcode, attr, input_shape, device, commit, commitdate)
    
    return jsonify(layer.get_best_optim()), 200

@bp.route('/get_all_optim')
def get_all_optim():
    """return best optims for each group

    Returns:
        List[Tuple[str, Dict]]: List of tuple of groupid and corresponding optim param
        int: response code
    """
    attr, device, input_shape, opcode, commit, groupid, commitdate = _common_info(request.json.get('data'))
    layer = get_or_create_layer(opcode, attr, input_shape, device, commit, commitdate)
    
    return jsonify(layer.get_all_optim()), 200

@bp.route('/get_profiles')
def get_latencies():
    attr, device, input_shape, opcode, commit, groupid, commitdate = _common_info(request.json.get('data'))
    
    layer = get_or_create_layer(opcode, attr, input_shape, device, commit, commitdate)
    
    return jsonify(layer.get_all_latencies(groupid)), 200

@bp.route('/initialize_latency', methods=['POST'])
def initialize_latency():
    data = request.json.get('data')
    attr, device, input_shape, opcode, commit, groupid, commitdate = _common_info(data)
    optim_param = data['optim_param']
    
    layer = get_or_create_layer(opcode, attr, input_shape, device, commit, commitdate)
    
    result = layer.initialize_latency(groupid, optim_param)
    
    return {}, 200