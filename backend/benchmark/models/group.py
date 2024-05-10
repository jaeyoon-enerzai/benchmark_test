import mongoengine as me
from models.device import DeviceFarm

class Latency(me.EmbeddedDocument):
    latency = me.FloatField()
    date = me.DateTimeField()
    
class GroupDB(me.Document):
    device = me.EnumField(DeviceFarm, required=True)
    group = me.StringField(required=True)
    median = me.FloatField()
    latencies = me.EmbeddedDocumentListField(Latency, default=[])
