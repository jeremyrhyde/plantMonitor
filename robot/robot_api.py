from flask import request, jsonify, json
from flask_api import FlaskAPI, status, exceptions
#from flask-cors import CORS
#from robot_config import *

app = FlaskAPI(__name__)
#CORS(app)

action_list = []
ready_list = []

# HOME PAGE
@app.route('/')
def home():
    return {'Robot API Homepage!':'Go to: BLE, ACTION, or DATE'}

# ACTION
@app.route('/command/', methods=['GET','POST'])
def action():

    if request.method == 'POST':
        data = request.data
        action = {'date': '', 'command': data['command'], 'para': data['para']}
        action_list.append(action)
        return {'command':'response'}

    if len(action_list) > 0:
        action_item = action_list.pop(0)
    else:
        action_item = {'date':'','command':'', 'para':''}

    return action_item

# ROBOT READY
@app.route('/robot_ready/', methods=['GET','POST'])
def robot_ready():

    if request.method == 'POST':
        data = request.data
        ready = {'ready': data['ready']}
        ready_list.append(ready)
        return {'ready':'no'}

    if len(ready_list) > 0:
        ready_item = ready_list.pop(0)
    else:
        ready_item = {'ready':'no'}

    return action_item

if __name__ == '__main__':
    print('STARTING API')
    app.run(host='0.0.0.0', port=5002)
