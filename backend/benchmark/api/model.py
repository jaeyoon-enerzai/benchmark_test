import random
import datetime
from flask import jsonify, Blueprint, request
from models.model import ModelDB
from models.device import DeviceFarm
from models.group import GroupDB

bp = Blueprint("model", __name__, url_prefix="/model")

@bp.route('/')
def get_all_models():
    models = ModelDB.objects()
    return jsonify(models), 200

def _common_info(data: dict):
    modelname = data['modelname']
    device = data['device']
    input_shape = data['input_shape']
    framework = data['framework']
    commit = data['commit']
    groupid = data['groupid']
    return modelname, device, input_shape, framework, commit, groupid

@bp.route('/get_latency')
def get_latency():
    data = request.json.get('data')
    modelname, device, input_shape, framework, commit, groupid = _common_info(data)
    
    group = GroupDB.objects(group=groupid).first()
    models = ModelDB.objects(modelname=modelname, framework=framework, 
                             input_shape=input_shape, device=device, commit=commit,
                             group=group)
    if len(models) == 1:
        return jsonify(models.first().get_latency()), 200
    else:
        raise RuntimeError("Model must be unique")

@bp.route('/upload_model', methods=['POST'])
def upload_model():
    data = request.json.get('data')
    modelname, device, input_shape, framework, commit, groupid = _common_info(data)
    
    latency = data['latency']
    date = datetime.datetime.fromtimestamp(data['date'])
    
    group = GroupDB.objects(group=groupid).first()
    models = ModelDB.objects(modelname=modelname, framework=framework, 
                             input_shape=input_shape, device=device, commit=commit,
                             group=group)
    if len(models) == 0:
        model = ModelDB(modelname=modelname, framework=framework,
                        input_shape=input_shape, device=device, commit=commit,
                        group=group)
        model.save()
    else:
        model = models.first()
    model.upload_model(date, latency)
    return {}, 200

# get the last commit
@bp.route('/last_commit')
def get_last_commit():
    data = request.json.get('data')
    modelname, device, input_shape, framework, commit, groupid = _common_info(data)
    
    latency = data['latency']
    date = datetime.datetime.fromtimestamp(data['date'])
    
    group = GroupDB.objects(group=groupid).first()
    models = ModelDB.objects(modelname=modelname, framework=framework, 
                             input_shape=input_shape, device=device, commit=commit,
                             group=group)

    sorted_models = sorted([(m_, m_.commitdate) for m_ in models], key=lambda t: t[1])[::-1]
    
    if len(sorted_models) > 1:
        return {'latest' : sorted_models[0].commit, 'second_latest' : sorted_models[1].commit}, 200
    else:
        return {'latest' : sorted_models[0].commit, 'second_latest' : None}, 200
        

# get result for a model
@bp.route('/get_all_result')
def get_all_result():
    data = request.json.get('data')
    modelname = data['modelname']
    device = data['device']
    input_shape = data['input_shape']
    framework = data['framework']
    
    models = ModelDB.objects(modelname=modelname, framework=framework, 
                             input_shape=input_shape, device=device)   
    result = {}
    for model in models:
        commit = model.commit
        group = model.group.group
        latdata = [(lat.date, lat.latency) for lat in  model.profile_stat.latencies]
        if group in result:
            result[group][commit] = (model.profile_stat.median, latdata)
        else:
            result[group] = {commit: (model.profile_stat.median, latdata)}
    return jsonify(result), 200
        