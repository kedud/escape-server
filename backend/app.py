# -*- coding: utf-8 -*-

from flask import Flask, jsonify, url_for, redirect, request
from flask_pymongo import PyMongo
from flask_restful import Api, Resource
from flask_cors import CORS

import datetime
import os

app = Flask(__name__)
app.config["MONGO_DBNAME"] = "nodes_db"
app.config["MONGO_URI"] = "mongodb://" + os.environ['MONGODB_USERNAME'] + ":" + os.environ['MONGODB_PASSWORD'] + "@" + os.environ['MONGODB_HOST'] + "/nodes"
mongo = PyMongo(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

APP_URL = "http://127.0.0.1:5000"


class Nodes(Resource):
    def get(self, id=None, hostname=None):
        data = []

        if id:
            node_info = mongo.db.nodes.find_one({"id": id}, {"_id": 0})
            if node_info:
                return jsonify({"status": "ok", "data": node_info})
            else:
                return {"response": "no node found for {}".format(id)}

        elif hostname:
            cursor = mongo.db.nodes.find({"hostname": hostname}, {"_id": 0}).limit(10)
            for node in cursor:
                node['url'] = APP_URL + url_for('nodes') + "/" + node.get('id')
                data.append(node)

            return jsonify({"hostname": hostname, "response": data})

        else:
            cursor = mongo.db.nodes.find({}, {"_id": 0, "update_time": 0}).limit(10)

            for node in cursor:
                print(node)
                node['url'] = APP_URL + url_for('nodes') + "/" + node.get('id')
                data.append(node)

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
api.add_resource(Nodes, "/node/<string:id>", endpoint="id")
api.add_resource(Nodes, "/node/hostname/<string:hostname>", endpoint="hostname")

@app.route('/register/<node>', methods=['POST'])
def register(node):
    print("name : ", node , '\tip:', request.remote_addr )
    return 'REGISTER SUCCESS'

@app.route('/<node>/alive', methods=['POST'])
def alive(node):
    print("name : ", node , '\tip:', request.remote_addr )
    return 'REGISTER SUCCESS'

@app.before_first_request
def startup():
    node_id = mongo.db.nodes.insert({"id": "sensor1", "hostname": "sensor1", "url": "http://127.0.0.1:5000/node/sensor1", "last_ping": datetime.datetime.now()});
    node_id = mongo.db.nodes.insert({"id": "sensor2", "hostname": "sensor2", "url": "http://127.0.0.1:5000/node/sensor2", "last_ping": datetime.datetime.now()});
    node_id = mongo.db.nodes.insert({"id": "sensor3", "hostname": "sensor3", "url": "http://127.0.0.1:5000/node/sensor3", "last_ping": datetime.datetime.now()});
    #print(node_id)
    print("fake nodes created")


if __name__ == "__main__":
    app.run(debug=True)