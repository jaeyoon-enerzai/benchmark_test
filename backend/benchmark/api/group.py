from models.group import GroupDB, Latency
import random, string
from flask import jsonify, Blueprint
from models.device import DeviceFarm
import datetime
import numpy as np

bp = Blueprint("group", __name__, url_prefix="/group")

def randomkey_generator():
    return ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(16)])

@bp.route('/')
def get_all_groups():
    groups = GroupDB.objects()
    return jsonify(groups), 200

@bp.route('/set_group')
def set_group():
    # TODO - parse from args
    device = DeviceFarm.LIME
    latency = random.random()
    date = datetime.datetime.now()
    
    tolerance = 0.15
    
    groups = GroupDB.objects(device=device)
    lat = Latency(latency=latency, date=date) 
    if len(groups) == 0:
        # empty group for the device
        groupkey = randomkey_generator()
        newgrp = GroupDB(device=device, group=groupkey, median=latency)
        newgrp.latencies.append(lat)
        newgrp.save()
        return jsonify({'group' : groupkey}), 200
    else:
        selected_diff_ratio = np.inf
        selected_group = None
        for group in groups:
            recorded_latency = group.median
            diff_ratio = abs(latency - recorded_latency) / recorded_latency
            if diff_ratio < tolerance:
                if diff_ratio < selected_diff_ratio:
                    selected_diff_ratio = diff_ratio
                    selected_group = group
        if selected_group is None:
            # No other group under tolerance -> this is a new group
            groupkey = randomkey_generator()
            existing_groups = [g_.group for g_ in groups]
            while groupkey in existing_groups:
                groupkey = randomkey_generator()
            newgrp = GroupDB(device=device, group=groupkey)
            selected_group = newgrp
        selected_group.latencies.append(lat)
        # median update
        selected_group.median = np.median([l_.latency for l_ in selected_group.latencies])
        selected_group.save()
        return jsonify({'group': selected_group.group}), 200
                                         