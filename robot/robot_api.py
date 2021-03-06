from flask import request, jsonify, json
from flask_api import FlaskAPI, status, exceptions
#from flask-cors import CORS
#from robot_config import *

app = FlaskAPI(__name__)
#CORS(app)

action_list = []

# HOME PAGE
@app.route('/')
def home():
    return {'Robot API Homepage!':'Go to: BLE, ACTION, or DATE'}

# ACTION
@app.route('/action/', methods=['GET','POST'])
def action():

    if request.method == 'POST':
        data = request.data
        action = {'Date': '', 'Action': data['action']}
        action_list.append(action)
        return {'Action':'response'}

    if len(action_list) > 0:
        action_item = action_list.pop(0)
    else:
        action_item = {'Date':'','Action':''}

    return action_item

if __name__ == '__main__':
    print('STARTING API')
    app.run(host='0.0.0.0', port=5002)
