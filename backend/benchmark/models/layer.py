from typing import Dict, Tuple
import mongoengine as me
from models.device import DeviceFarm
import numpy as np
import datetime
from utils import make_query_dict, tuple_to_list

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

class LayerDB(me.Document):
    opcode = me.StringField(required=True)
    attr = me.DictField(required=True)
    input_shape = me.ListField(required=True)
    device = me.EnumField(DeviceFarm, required=True)
    commit = me.StringField()
    commitdate = me.DateTimeField()
    
    profile_stat = me.DictField(me.EmbeddedDocumentField(LayerStat))
    best_optim = me.DictField()

    def set_best_optim(self):
        # find the latest group of profile
        profiles = self.profile_stat
        _, latest_groupid = max([[p_.last_modified, groupid_] for groupid_, p_ in profiles.items()], key=lambda t: t[0])
        
        # check if the latest group has all best optim from other groups
        last_modified_profile = self.profile_stat.get(latest_groupid)
        for groupid, profile in profiles.items():
            if groupid != latest_groupid:
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
    
    def get_group_represent(self):
        representative = dict()
        for groupid, profile in self.profile_stat.items():
            representative[groupid] = profile.best_optim
        return representative
    
    def set_group(self, profiled_dict : Dict[int, Tuple[Dict, float]]):
        selected_diff_ratio = np.inf
        selected_group = None
        for groupid, (optim_param, profiled_latency) in profiled_dict.items():
            measured_latency = self._get_profile(groupid, optim_param).median
            diff_ratio = abs(profiled_latency - measured_latency) / measured_latency
            if diff_ratio < 0.15:
                # tolerance is 15%
                if diff_ratio < selected_diff_ratio:
                    selected_diff_ratio = diff_ratio
                    selected_group = groupid
        if selected_group is None:
            # No other group under 15% difference -> this is a new group
            existing_groups = [int(k_) for k_ in self.profile_stat.keys()]
            for n_ in range(len(existing_groups)+1):
                if n_ not in existing_groups:
                    newgrp = n_
                    break
            selected_group = str(newgrp)
        for _, (optim_param, profiled_latency) in profiled_dict.items():
            self.upload_latency(selected_group, optim_param, datetime.datetime.now(), profiled_latency)
        return selected_group
        
    def initialize_group(self, groupid:int):
        self.profile_stat.pop(groupid)
        self.save()
    
    def _get_profile(self, groupid:int, optim_param: Dict):
        profile_stat = self.profile_stat.get(groupid) # LayerStat
        optim_param = tuple_to_list(optim_param)
        selected_profiles = [profile for profile in profile_stat.profiles if profile.optim_param == optim_param]
        return selected_profiles
    
    def _group_exist(self, groupid):
        profile_stat = self.profile_stat.get(groupid)
        return (profile_stat is not None)
        
    def _create_group(self, groupid):
        try:
            int(groupid)
        except ValueError:
            raise ValueError("groupid must be a string of integer")
        self.profile_stat[groupid] = LayerStat(last_modified=datetime.datetime.now())
        
    def initialize_latency(self, groupid:int, optim_param: Dict):
        selected_profiles = self._get_profile(groupid, optim_param)
        for pr in selected_profiles:
            Profile.objects(id=pr.id).delete()
            
    def upload_latency(self, groupid, optim_param, date, latency):
        if not self._group_exist(groupid):
            self._create_group(groupid)
        selected_profiles = self._get_profile(groupid, optim_param)
        if len(selected_profiles) == 0:
            profile = Profile(optim_param=optim_param, median=latency,
                            )
            profile.latencies = [Latency(date=date, latency=latency)]
            profile.save()
            self.profile_stat.get(groupid).profiles.append(profile)
            self.profile_stat.get(groupid).last_modified = datetime.datetime.now()
            self.save()
        elif len(selected_profiles) == 1:
            profile = Profile.objects(id=selected_profiles[0].id).first()
            profile.latencies.append(Latency(date=date, latency=latency))
            profile.median = np.median([l_.latency for l_ in profile.latencies])
            profile.save()
            self.profile_stat.get(groupid).last_modified = datetime.datetime.now()
            self.save()
        else:
            raise RuntimeError("profile has unique optim param but has more than one")
        