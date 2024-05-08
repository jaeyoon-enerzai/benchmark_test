from flask import Flask, jsonify
from flask_mongoengine import MongoEngine
from mongoengine import connect
from models import Layer, ModelDB, ModelStat, DateLatency, LayerStat, DeviceFarm, Movie, Imdb
from typing import Dict
from werkzeug.exceptions import BadRequest
import sys


print("SFFFUCCK")

app = Flask(__name__)

app.config['MONGODB_SETTINGS'] = {
    'db': 'benchmark',
    'host': 'db',
    'port': 27017
}
MONGODB_URL = "mongodb://localhost/benchmark"
db = MongoEngine()
db.init_app(app)

@app.route('/movies')
def get_movies():
    movies = Movie.objects()
    return jsonify(movies), 200

@app.route('/')
def hello():
    try:
        bttf = Movie(title='Back to the Future')
        bttf.imdb = Imdb(imdb_id='tdfd', votes=12)
        bttf.save()
    except Exception as e:
        print("Ooho", flush=True)
        raise e
    # layer = Layer.objects(opcode='abc')
    layer = Movie.objects(title='Back to the Future')
    print(layer)
    print("This is output1", flush=True)
    print("dd", flush=True)
    return {'a':'d'}

@app.route('/abc')
def hello2():
    return {'a':'e'}

def build_layer_result(data: Dict) -> Layer:
    result = Layer()
    opcode = data['opcode']
    attr = data['attr']
    device = data['device']
    
    commit = data['commit']
    datetime = data['datetime']
    profile_stat = data['profile_stat']
    
    # if exists
    layer = Layer.objects(opcode=opcode, attr=attr, device=device)
    print(layer)
    

@app.route('/result', methods=['POST'])
def upload_layer():
    data = request.json.get('data')
    
    if data is None:
        raise BadRequest("omitted required data")
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)