# -*- coding: utf-8 -*-

from flask import Flask, jsonify, url_for, redirect, request
from flask_restful import Api, Resource
from flask_cors import CORS

from tinydb import TinyDB, Query
from tinyrecord import transaction

from flask_socketio import SocketIO, emit
import requests

import datetime
import os
import json

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

db = TinyDB(os.environ['PROJECT_PATH'] + 'nodes.json')

socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")

APP_URL = "http://127.0.0.1:5000"

def is_a_sensor(node_json):
    return "sensor" in node_json["types"]


def is_solved(node_json):
    return node_json["status"] == "solved"

def execute_scenario_for(sensor_hostname=None):

    scenarios_json = None
    with open(os.environ['PROJECT_PATH'] + "scenarios.json", "r") as f:
        scenarios_json = json.load(f)

    scenarios = scenarios_json["scenarios"]

    for scenario in scenarios:
        if scenario["sensor_solved"] == sensor_hostname:
            if (scenario["actuator_triggered"]):
                actuate(scenario["actuator_triggered"])


def actuate(hostname):
    if hostname:
        with transaction(db) as tr:
            query = Query()
            node = db.search(query.hostname == hostname)
            if len(node):
                print(node[0])
                r = requests.get(node[0]["url"] + '/actuate')
                print(r)


class Nodes(Resource):
    
    def get_one_node_data(self, hostname):
        data = []
        cursor = None
        Node = Query()
        cursor = tr.search(Node.hostname == hostname)

        for node in cursor:
            node["id"] = node["hostname"]
            data.append(node)

        return data

    def get_all_nodes_data(self):
        data = []
        cursor = db.all()
        for node in cursor:
            print(node)
            node["id"] = node["hostname"]
            data.append(node)
        return data

    def get(self, hostname=None):
        data = []
        if hostname:
            return jsonify({"hostname": hostname, "response": self.get_one_node_data(hostname)})

        else:
            data = self.get_all_nodes_data()
            print(data)
            return jsonify({"response": data})

    def post(self):
        node_data = request.get_json()

        if not node_data:
            node_data = {"response": "ERROR"}
            return jsonify(node_data)

        hostname = node_data.get('hostname')
        node_data["last_ping"] = int(datetime.datetime.now().timestamp())
        node_data["url"] = 'http://' + node_data['ip']

        if not hostname:
            return {"response": "id number missing"}
            
        with transaction(db) as tr:
            Node = Query()
            nodes = db.search(Node.hostname == hostname)
            was_solved = False
            if len(nodes) > 0:
                node = nodes[0]
                was_solved = is_solved(node)
                tr.update(node_data, Node.hostname == hostname)
            else:
                tr.insert(node_data)

        client_node = { 
            "hostname": node_data["hostname"],
            "last_ping": node_data["last_ping"],
            "ip": node_data["ip"],
            "url": node_data["url"],
            "status": node_data["status"],
            "types": node_data["types"]
        }
        print (json.dumps(client_node, default=str))
        socketio.emit(node_data["hostname"], json.dumps(client_node, default=str))
        
        if is_a_sensor(client_node) and is_solved(client_node) and not was_solved:
            execute_scenario_for(client_node["hostname"])

        return {"response": "node updated."}

    def delete(self, id):
        with transaction(db) as tr:
            Node = Query()
            tr.remove(Node.id == id)

        return redirect(url_for("nodes"))


class Index(Resource):
    def get(self):
        return redirect(url_for("nodes"))
    def post(self):
        return redirect(url_for("nodes"))


api = Api(app)
api.add_resource(Nodes, "/", endpoint="index")
api.add_resource(Nodes, "/node", endpoint="nodes")
api.add_resource(Nodes, "/node/<string:hostname>", endpoint="hostname")

def add_unique_test_sensor_to_db(sensor_name):
    test_sensor =  { 
        "hostname": "test_" + sensor_name,
        "url": "http://127.0.0.1:5000/node/"+sensor_name, 
        "last_ping": 0,
        "status": "resolved"
        }
    with transaction(db) as tr:
        Node = Query()
        tr.remove(Node.hostname == test_sensor["hostname"])
        tr.insert(test_sensor)


@app.before_first_request
def startup():
    add_unique_test_sensor_to_db("sensor1")
    add_unique_test_sensor_to_db("sensor2")
    add_unique_test_sensor_to_db("sensor3")
    print("fake nodes created")

@socketio.on('connect')
def onSocketIoConnect():
    print('Client connected')

@socketio.on('disconnect')
def onSocketIoDisconnect():
    print('Client disconnected')

@socketio.on('action')
def socketio_action(data):
    print(data)
    hostname = data["hostname"]
    print(hostname)
    actuate(hostname)


@socketio.on('reboot')
def socketio_action(data):
    print(data)
    hostname = data["hostname"]
    print(hostname)
    if hostname:
        q = []
        with transaction(db) as tr:
            Node = Query()
            q = db.search(Node.hostname == hostname)

        if len(q) > 0 :
            r = requests.get(q[0]["url"] + '/reboot')

if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0")
