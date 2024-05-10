from flask import jsonify, Blueprint
from models.device import DeviceFarm
import datetime

bp = Blueprint("model", __name__, url_prefix="/model")
