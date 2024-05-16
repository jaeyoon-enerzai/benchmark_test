import mongoengine as me
from models.device import DeviceFarm
import uuid

class Latency(me.EmbeddedDocument):
    latency = me.FloatField()
    date = me.DateTimeField()
    
class GroupDB(me.Document):
    device = me.EnumField(DeviceFarm, required=True)
    group = me.StringField(unique=True, default=lambda: str(uuid.uuid4()))
    median = me.FloatField()
    latencies = me.EmbeddedDocumentListField(Latency, default=[])
