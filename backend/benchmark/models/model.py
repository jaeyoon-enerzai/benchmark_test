from models.device import DeviceFarm
from models.group import GroupDB
import datetime
import mongoengine as me



class Latency(me.EmbeddedDocument):
    date= me.DateTimeField()
    latency = me.FloatField()
    
class Profile(me.EmbeddedDocument):
    median = me.FloatField()
    latencies = me.EmbeddedDocumentListField(Latency, default= [])

class ModelDB(me.Document):
    modelname = me.StringField(required=True)
    framework = me.StringField(required=True) # Pytorch, Tflite, etc..and
    input_shape = me.ListField(required=True)
    device = me.EnumField(DeviceFarm, required=True)
    commit = me.StringField()
    commitdate = me.DateTimeField()
    group = me.ReferenceField(GroupDB)
    profile_stat = me.EmbeddedDocumentField(Profile)
    
    def upload_model(self, date, latency):
        if self.profile_stat is None:
            self.profile_stat = Profile()
        self.profile_stat.latencies.append(Latency(date=date, latency=latency))
        self.save()
    
    def get_latency(self):
        return {'median': self.profile_stat.median, 
                'latencies': [{'date': l_.date, 'latency': l_.latency} for l_ in self.profile_stat.latencies]}