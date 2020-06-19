# -*- coding: utf-8 -*-

from flask import Flask, jsonify, url_for, redirect, request
from flask_restful import Api, Resource
from flask_cors import CORS

from tinydb import TinyDB, Query

from flask_socketio import SocketIO, emit
import requests

import datetime
import os
import json
import scenario
from bson import json_util

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

db = TinyDB('./nodes.json')

socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")

APP_URL = "http://127.0.0.1:5000"

def check_scenario(hostname=None):
    for node in scenario.nodes:
        print(node["hostname"])
        if node["hostname"] == hostname:
            print("actuate")
            if (node["trigger"]):
                actuate(node["trigger"])
            return
    return
#    if nodeName && nodes[nodeName] :

def actuate(hostname):
    if hostname:
        query = Query()
        node = db.search(query.hostname == hostname)
        if len(node):
            print(node[0])
            r = requests.get(node[0]["url"] + '/actuate')
            print(r)


class Nodes(Resource):
    def get(self, hostname=None):
        data = []
        if hostname:
            Node = Query()
            cursor = db.search(Node.hostname == hostname)
            for node in cursor:
                #node['url'] = APP_URL + url_for('nodes') + "/" + node.get('id')
                node["id"] = node["hostname"]
                data.append(node)

            return jsonify({"hostname": hostname, "response": data})

        else:
            cursor = db.all()
            for node in cursor:
                print(node)
                #node['url'] = APP_URL + url_for('nodes') + "/" + node.get('id')
                node["id"] = node["hostname"]
                data.append(node)
            print(data)
            return jsonify({"response": data})

    def post(self):
        node_data = request.get_json()
        if not node_data:
            node_data = {"response": "ERROR"}
            return jsonify(node_data)
        else:
            hostname = node_data.get('hostname')
            node_data["last_ping"] = int(datetime.datetime.now().timestamp())
            node_data["url"] = 'http://' + node_data['ip']
            Node = Query()
            if hostname:
                if db.search(Node.hostname == hostname):
                    db.update(node_data ,Node.hostname == hostname)
                    #mongo.db.nodes.update({'hostname': hostname}, {'$set': node_data})

                else:
                    db.insert(node_data)
                    #mongo.db.nodes.insert(node_data)

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
                return {"response": "node updated."}
            else:
                return {"response": "id number missing"}

        return {"response": "updated"}

    # def put(self, id):
    #     data = request.get_json()
    #     data["last_ping"] = datetime.datetime.now()
    #     mongo.db.nodes.update({'id': id}, {'$set': data})
    #     return redirect(url_for("nodes"))

    def delete(self, id):
        Node = Query()
        db.remove(Node.id == id)
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

@app.before_first_request
def startup():
    test_sensor =  { 
        "hostname": "test_sensor1",
        "url": "http://127.0.0.1:5000/node/sensor1", 
        "last_ping": 0
        }
    db.insert(test_sensor)
    
    # mongo.db.nodes.update(
    #     {"hostname": "sensor2"},
    #     { 
    #     "hostname": "sensor2",
    #     "url": "http://127.0.0.1:5000/node/sensor2", 
    #     "last_ping": datetime.datetime.now()},
    #     upsert=True
    # )
    # mongo.db.nodes.update(
    #     {"hostname": "sensor3"},
    #     { 
    #     "hostname": "sensor3",
    #     "url": "http://127.0.0.1:5000/node/sensor3", 
    #     "last_ping": datetime.datetime.now()},
    #     upsert=True
    # )
    print("fake nodes created")
    print(scenario.nodes)
    check_scenario("cat")

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
        node = mongo.db.nodes.find_one({"hostname": hostname})
        if node:
            print(node)
            r = requests.get(node["url"] + '/reboot')
            print(r)

if __name__ == "__main__":
    socketio.run(app, debug=True)
    #app.run(debug=True)
