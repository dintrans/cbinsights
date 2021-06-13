import validators
import config
from flask import Flask, request, Response
from flask import json
from CustomTtlCache import CustomTTLCache
from dotenv import dotenv_values

app = Flask(__name__)

"""Check if the parameters in the .env are valid"""
setup = dotenv_values()
for parameter in config.parameters.keys():
    if setup.get(parameter):
        try:
            val = config.parameters_validator[parameter](setup.get(parameter))
            config.parameters[parameter] = val
        except ValueError:
            app.logger.warning(f"{setup.get(parameter)} is not a valid {parameter} value, default value {str(config.parameters[parameter])} was used instead")
    else:
        app.logger.info(f"Value for {parameter} not found on the environment, default value {str(config.parameters[parameter])} was used instead")

"""Create the cache instance"""
cache = CustomTTLCache(
    config.parameters['CACHE_SLOTS'],
    config.parameters['OBJECT_TTL'],
    config.eviction_policy_translator[config.parameters['EVICTION_POLICY']]
)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/object/<int:key>", methods=['GET'])
def object_retrieve(key):
    try:
        c = cache[key]
    except KeyError:
        return Response("", status=404)
    return Response(c, status=200, mimetype='application/json')


@app.route("/object/<int:key>", methods=['DELETE'])
def object_delete(key):
    try:
        del cache[key]
    except KeyError:
        return Response("", status=404)
    return Response("", status=200)


@app.route("/object/<int:key>", methods=['POST', 'PUT'])
def object_create(key):
    try:
        t = requests.args.get('ttl', '')
        ttl = -1 if t is '' else int(t)
        value = json.dumps(json.loads(request.get_data()))
    except ValueError as e:
        return Response("", status=400)
    try:
        cache.__setitem__(key, value, ttl)
    except KeyError:
        return Response("", status=507)
    return Response("", status=200)

if __name__ == '__main__':
    app.run()
