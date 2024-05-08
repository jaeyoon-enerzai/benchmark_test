import mongoengine as me
import enum

class Imdb(me.EmbeddedDocument):
    imdb_id = me.StringField()
    rating = me.DecimalField()
    votes = me.IntField()
    
class Movie(me.Document):
    title = me.StringField(required=True)
    year = me.IntField()
    rated = me.StringField()
    poster = me.FileField()
    imdb = me.EmbeddedDocumentField(Imdb)



class DeviceFarm(enum.Flag):
    AVOCADO = enum.auto()
    BLUEBERYY = enum.auto()
    CARROT = enum.auto()
    DURIAN = enum.auto()
    EGGPLANT = enum.auto()
    FIG = enum.auto()
    GUAVA = enum.auto()
    HAZELNUT = enum.auto()
    ICEMANGO = enum.auto()
    JUJUBE = enum.auto()
    LIME = enum.auto()
    MANDARIN = enum.auto()
    NUTMEG = enum.auto()
    OLIVE = enum.auto()
    PINEAPPLE = enum.auto()

class LayerStat(me.EmbeddedDocument):
    optim_param = me.DictField()
    latency = me.FloatField()
    commit = me.StringField()
    datetime = me.DateTimeField()

class DateLatency(me.EmbeddedDocument):
    date = me.DateTimeField()
    latency = me.FloatField()

class ModelStat(me.EmbeddedDocument):
    datelatency = me.EmbeddedDocumentListField(DateLatency, null=True)

class Layer(me.Document):
    opcode = me.StringField(required=True)
    attr = me.DictField(required=True)
    device = me.EnumField(DeviceFarm, required=True)
    profile_stat = me.EmbeddedDocumentListField(LayerStat, null=True)
    best_optim = me.DictField()
    
class ModelDB(me.Document):
    modelname = me.StringField(required=True)
    device = me.EnumField(DeviceFarm, required=True)
    commit = me.StringField(required=True)
    latency = me.EmbeddedDocumentListField(ModelStat, null=True)
    baseline_latency = me.DictField(me.EmbeddedDocumentListField(ModelStat, null=True))
    # layerwise_latency