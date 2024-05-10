from flask import Flask
from flask_mongoengine import MongoEngine
from mongoengine import connect
from api import layer_bp, model_bp, group_bp
from werkzeug.exceptions import BadRequest

app = Flask(__name__)

app.config['MONGODB_SETTINGS'] = {
    'db': 'benchmark',
    'host': 'db',
    'port': 27017
}
MONGODB_URL = "mongodb://localhost/benchmark"
db = MongoEngine()
db.init_app(app)

app.register_blueprint(layer_bp)
app.register_blueprint(model_bp)
app.register_blueprint(group_bp)

# @app.route('/modelupload')
# def upload_model():
#     model = ModelDB(modelname="mobilenet")
#     device = DeviceFarm.AVOCADO
#     model.device = device
#     model.commit = "abcdef"
    
#     repeatnum = random.randint(1,5)
#     modelstat = ModelStat()
#     for _ in range(repeatnum):
#         date = datetime.datetime.now()
#         latency = random.random()
#         modelrun_onetime = DateLatency(date=date, latency=latency)
#         modelstat.datelatency.append(modelrun_onetime)
#     model.latency = modelstat
    
#     for baseline in ['tf', 'openvino', 'torch']:
#         if random.random() > 0.5:
#             repeatnum = random.randint(1,5)
#             modelstat = ModelStat()
#             for _ in range(repeatnum):
#                 date = datetime.datetime.now()
#                 latency = random.random()
#                 modelrun_onetime = DateLatency(date=date, latency=latency)
#                 modelstat.datelatency.append(modelrun_onetime)
#             model.baseline_latency[baseline] = modelstat
#     model.save()
#     return jsonify(model), 200





    
""" @app.route('/result', methods=['POST'])
def upload_layer():
    data = request.json.get('data')
    
    if data is None:
        raise BadRequest("omitted required data")
 """    
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)