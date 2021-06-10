import validators
from flask import Flask, request
from flask import json
from CustomTTLCache import CustomTTLCache
from dotenv import dotenv_values

app = Flask(__name__)

config = dotenv_values()
config_parameters = {'CACHE_SLOTS': 10000, 'OBJECT_TTL': 3600, 'EVICTION_POLICY': "REJECT"}
config_parameters_validators = {
    'CACHE_SLOTS': lambda x : validators.positive_int_validator(x), 
    'OBJECT_TTL': lambda x : validators.positive_int_validator(x), 
    'EVICTION_POLICY': lambda x : validators.string_in_array_validator(x,["OLDEST_FIRST","NEWEST_FIRST","REJECT"]),
}
eviction_policy_translator = {
    'OLDEST_FIRST': 'FIFO',
    'NEWEST_FIRST': 'LIFO',
    'REJECT': 'Reject',
}
for parameter in config_parameters_validators.keys():
    if config.get(parameter):
        try:
            val = config_parameters_validators[parameter](config.get(parameter))
            config_parameters[parameter]=val
        except ValueError:
            print(" * WARNING: "+config.get(parameter)+" is not a valid "+parameter+" value, default value "+str(config_parameters[parameter])+" was used instead")
    else:
        print(" * Value for "+parameter+" not found on the environment, default value "+config_parameters[parameter]+" was used instead")
cache = CustomTTLCache(config_parameters['CACHE_SLOTS'], config_parameters['OBJECT_TTL'], eviction_policy_translator[config_parameters['EVICTION_POLICY']])

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/object/<int:key>", methods=['GET','POST','PUT','DELETE'])
def object(key):
    if request.method == 'GET':
        return f'<p>Yes, the number {key}</p>'
    elif request.method == 'DELETE':
        cache.__delitem__(key)
    elif request.method in ['POST','PUT']:
        try:
            ttl = -1 if request.args.get('ttl','') is '' else int(request.args.get('ttl',''))
            value = json.dumps(json.loads(request.get_data()))
        except ValueError as e:
            return "400 Bad Request"
        print('TTL: '+str(ttl))
        print(value)
        cache.__setitem__(key,value,ttl)
        return '200 OK'

"""
cache = {}

@app.route("/create")
def create():
    cache['foo'] = 0
    return jsonify(cache['foo'])

@app.route("/increment")
def increment():
    cache['foo'] = cache['foo'] + 1
    return jsonify(cache['foo'])

@app.route("/read")
def read():
    return jsonify(cache['foo'])"""

if __name__ == '__main__':
    app.run()