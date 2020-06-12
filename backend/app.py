# -*- coding: utf-8 -*-

from flask import Flask, jsonify, url_for, redirect, request
from flask_pymongo import PyMongo
from flask_restful import Api, Resource
from flask_cors import CORS

from flask_socketio import SocketIO, emit
import requests

import datetime
import os
import json
from bson import json_util

app = Flask(__name__)
app.config["MONGO_DBNAME"] = "nodes_db"
app.config["MONGO_URI"] = "mongodb://" + os.environ['MONGODB_USERNAME'] + ":" + os.environ['MONGODB_PASSWORD'] + "@" + os.environ['MONGODB_HOST'] + "/nodes"
mongo = PyMongo(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")

APP_URL = "http://127.0.0.1:5000"


class Nodes(Resource):
    def get(self, hostname=None):
        data = []
        if hostname:
            cursor = mongo.db.nodes.find({"hostname": hostname}, {"_id": 0}).limit(10)
            for node in cursor:
                #node['url'] = APP_URL + url_for('nodes') + "/" + node.get('id')
                node["id"] = node["hostname"]
                data.append(node)

            return jsonify({"hostname": hostname, "response": data})

        else:
            cursor = mongo.db.nodes.find({}, {"_id": 0, "update_time": 0}).limit(10)

            for node in cursor:
                print(node)
                #node['url'] = APP_URL + url_for('nodes') + "/" + node.get('id')
                node["id"] = node["hostname"]
                data.append(node)
            print(data)
            return jsonify({"response": data})

    def post(self):
        data = request.get_json()
        if not data:
            data = {"response": "ERROR"}
            return jsonify(data)
        else:
            id = data.get('id')
            data["last_ping"] = datetime.datetime.now()
            if id:
                if mongo.db.nodes.find_one({"id": id}):
                    mongo.db.nodes.update({'id': id}, {'$set': data})
                    return {"response": "node already exists."}

                else:
                    mongo.db.nodes.insert(data)
            else:
                return {"response": "id number missing"}

        return redirect(url_for("nodes"))

    def put(self, id):
        data = request.get_json()
        data["last_ping"] = datetime.datetime.now()
        mongo.db.nodes.update({'id': id}, {'$set': data})
        return redirect(url_for("nodes"))

    def delete(self, id):
        mongo.db.nodes.remove({'id': id})
        return redirect(url_for("nodes"))


class Index(Resource):
    def get(self):
        return redirect(url_for("nodes"))


api = Api(app)
api.add_resource(Index, "/", endpoint="index")
api.add_resource(Nodes, "/node", endpoint="nodes")
api.add_resource(Nodes, "/node/<string:hostname>", endpoint="hostname")

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    print("data : ", data)
    if not data:
        data = {"response": "ERROR"}
        return jsonify(data)
    else:
        hostname = data.get('hostname')
        ip = data.get('ip')
        data["last_ping"] = datetime.datetime.now()
        data["ip"] = ip
        data["url"] = 'http://' + ip
        data["status"] = "unsolved"
        if hostname:
            if mongo.db.nodes.find_one({"hostname": hostname}):
                mongo.db.nodes.update({'hostname': hostname}, {'$set': data})
                return {"response": "node already exists."}
            else:
                mongo.db.nodes.insert(data)
        else:
            return {"response": "hostname missing"}

    data = {"response": "success"}
    return jsonify(data)

@app.route('/<hostname>/alive', methods=['POST'])
def alive(hostname):
    if hostname:
        node = mongo.db.nodes.find_one({"hostname": hostname})
        if node:
            node["last_ping"] = datetime.datetime.now()
            #node["ip"] = request.remote_addr
            #node["url"] = 'http://' + request.remote_addr
            mongo.db.nodes.update_one({'hostname': hostname}, {'$set': node})
            client_node = { 
                "hostname": node["hostname"],
                "last_ping": node["last_ping"],
                "ip": node["ip"],
                "url": node["url"],
                "status": node["status"]
            }
            print (json.dumps(client_node, default=str))
            socketio.emit(node["hostname"], json.dumps(client_node, default=str))
            return {"response": "node already exists."}
        else:
            data = {"response": "node not found"}
            return jsonify(data)

    else:
        data = {"response": "ERROR"}
        return jsonify(data)

@app.route('/<hostname>/update', methods=['POST'])
def update(hostname):
    print("update: " +  hostname)
    data = request.get_json()
    print(data)
    if hostname:
        node = mongo.db.nodes.find_one({"hostname": hostname})
        if node:
            node["last_ping"] = datetime.datetime.now()
            #node["ip"] = request.remote_addr
            node["status"] = data["status"]
            mongo.db.nodes.update_one({'hostname': hostname}, {'$set': node})
            client_node = { 
                "hostname": node["hostname"],
                "last_ping": node["last_ping"],
                "ip": node["ip"],
                "url": node["url"],
                "status": data["status"]
            }
            if hostname:
                r = requests.get(node["url"] + '/actuate')
            print (json.dumps(client_node, default=str))
            socketio.emit(node["hostname"], json.dumps(client_node, default=str))
            return {"response": "node already exists."}
        else:
            data = {"response": "node not found"}
            return jsonify(data)

    else:
        data = {"response": "ERROR"}
        return jsonify(data)

@app.before_first_request
def startup():
    mongo.db.nodes.update(
        {"hostname": "sensor1"},
        { 
        "hostname": "sensor1",
        "url": "http://127.0.0.1:5000/node/sensor1", 
        "last_ping": datetime.datetime.now()},
        upsert=True
    )
    mongo.db.nodes.update(
        {"hostname": "sensor2"},
        { 
        "hostname": "sensor2",
        "url": "http://127.0.0.1:5000/node/sensor2", 
        "last_ping": datetime.datetime.now()},
        upsert=True
    )
    mongo.db.nodes.update(
        {"hostname": "sensor3"},
        { 
        "hostname": "sensor3",
        "url": "http://127.0.0.1:5000/node/sensor3", 
        "last_ping": datetime.datetime.now()},
        upsert=True
    )
    print("fake nodes created")

@socketio.on('connect')
def test_connect():
    print('Client connected')

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

@socketio.on('action')
def socketio_action(data):
    print(data)
    hostname = data["hostname"]
    print(hostname)
    if hostname:
        node = mongo.db.nodes.find_one({"hostname": hostname})
        if node:
            print(node)
            r = requests.get(node["url"] + '/actuate')
            print(r)


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
