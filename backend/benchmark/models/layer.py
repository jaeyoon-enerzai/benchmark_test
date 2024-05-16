from typing import Dict, Tuple, List
import mongoengine as me
from models.device import DeviceFarm
from models.group import GroupDB
import numpy as np
import datetime
from models.utils import tuple_to_list, make_query_dict

def get_layers(opcode, attr, input_shape, device) -> List:
    # get all layer for any commit
    # if not exists, do not create
    querydict = make_query_dict(attr, "attr")
    querydict['input_shape'] = input_shape
    querydict['opcode'] = opcode
    querydict['device'] = device
    return LayerDB.objects(**querydict)

def get_or_create_layer(opcode, attr, input_shape, device, commit, commitdate):
    # find if a layer exists or not
    querydict = make_query_dict(attr, "attr")
    querydict['input_shape'] = input_shape
    querydict['opcode'] = opcode
    querydict['device'] = device
    querydict['commit'] = commit

    layer = LayerDB.objects(**querydict)
    if len(layer) == 0:
        layer = LayerDB(opcode=opcode, device=device, input_shape = input_shape, commit=commit, commitdate=commitdate)
        for k_, v_ in attr.items():
            layer.attr[k_] = v_
        layer.save()
    elif len(layer) == 1:
        layer = layer[0]
    else:
        raise RuntimeError("Layer must be unique but there are more than one")
    return layer

class Latency(me.EmbeddedDocument):
    date = me.DateTimeField()
    latency = me.FloatField() 

class Profile(me.Document):
    optim_param = me.DictField()
    median = me.FloatField()
    latencies = me.EmbeddedDocumentListField(Latency, default=[])

class LayerStat(me.EmbeddedDocument):
    last_modified = me.DateTimeField()
    best_optim = me.DictField()
    profiles = me.ListField(me.ReferenceField(Profile))
    group = me.ReferenceField(GroupDB)

class LayerDB(me.Document):
    opcode = me.StringField(required=True)
    attr = me.DictField(required=True)
    input_shape = me.ListField(required=True)
    device = me.EnumField(DeviceFarm, required=True)
    commit = me.StringField()
    commitdate = me.DateTimeField()
    
    profile_stat = me.ListField(me.EmbeddedDocumentField(LayerStat))
    best_optim = me.DictField()

    def set_best_optim(self):
        # find the latest group of profile
        profiles = self.profile_stat
        last_modified_profile = max(profiles, key=lambda t: t.last_modified)
        latest_groupid = last_modified_profile.group.group
        
        # check if the latest group has all best optim from other groups
        for profile in profiles:
            if profile.group.group != latest_groupid:
                other_best_optim = profile.best_optim
                other_best_optim_profile = self._get_profile(latest_groupid, other_best_optim)
                if len(other_best_optim_profile) == 0:
                    raise RuntimeError("The current group must contains all best optim from other group but does not. Should call set_group first")
                elif len(other_best_optim_profile) > 1:
                    raise RuntimeError("Profile must have unique optim param but there are more than one")
        # set the best optim
        new_optim_param = min(last_modified_profile.profiles, key=lambda t: t.median).optim_param
        last_modified_profile.best_optim = new_optim_param
        self.best_optim = new_optim_param
        self.save()
    
    def get_best_optim(self):
        return self.best_optim
    
    def get_all_optim(self):
        optims = []
        for profile in self.profile_stat:
            optims.append((profile.group.group, profile.best_optim))
        return optims
    
    def get_group_represent(self):
        representative = dict()
        for profile in self.profile_stat:
            representative[profile.group.group] = profile.best_optim
        return representative
            
    def initialize_group(self, groupid:str):
        raise NotImplementedError
        self.profile_stat.pop(groupid)
        self.save()
    
    def _get_profile(self, groupid:str, optim_param: Dict):
        profile_stat = self._get_stat(groupid) # LayerStat
        optim_param = tuple_to_list(optim_param)
        selected_profiles = [profile for profile in profile_stat.profiles if profile.optim_param == optim_param]
        return selected_profiles
    
    def _get_stat(self, groupid):
        """
        get LayerStat object from groupid if exists otherwise return None
        """
        stats = [stat_ for stat_ in self.profile_stat if stat_.group.group == groupid]
        if len(stats) == 0:
            return None
        elif len(stats) == 1:
            return stats[0]
        else:
            raise RuntimeError("groupid should be unique")
                
    def get_all_latencies(self, groupid : str):
        stat = self._get_stat(groupid)
        if stat is None:
            # empty profiles
            return []
        else:
            return [(prof.optim_param, prof.median) for prof in stat.profiles]
             
        
    def initialize_latency(self, groupid:str, optim_param: Dict):
        selected_profiles = self._get_profile(groupid, optim_param)
        stat = self._get_stat(groupid)
        rm_ids = []
        for pr in selected_profiles:
            objid = pr.id
            Profile.objects(id=objid).delete()
            rm_ids.append(objid)
        stat.profiles = [prof for prof in stat.profiles if (prof.id) not in rm_ids]
        self.save()
            
    def upload_latency(self, groupid, optim_param, date, latency):
        stat = self._get_stat(groupid)
        if stat is None:
            stat = LayerStat(last_modified=datetime.datetime.now(), group=GroupDB.objects(group=groupid).first())
            self.profile_stat.append(stat)
            self.save()
        selected_profiles = self._get_profile(groupid, optim_param)
        if len(selected_profiles) == 0:
            profile = Profile(optim_param=optim_param, median=latency)
            profile.latencies = [Latency(date=date, latency=latency)]
            profile.save()
            stat.profiles.append(profile)
            stat.last_modified = datetime.datetime.now()
            self.save()
        elif len(selected_profiles) == 1:
            profile = Profile.objects(id=selected_profiles[0].id).first()
            profile.latencies.append(Latency(date=date, latency=latency))
            profile.median = np.median([l_.latency for l_ in profile.latencies])
            profile.save()
            stat.last_modified = datetime.datetime.now()
            self.save()
        else:
            raise RuntimeError("profile has unique optim param but has more than one")
        