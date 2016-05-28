#!/usr/bin/env python
# __author__ = u"james.morris"
from flask import Flask, jsonify

app = Flask(__name__)

tasks = [
    {
        u"id": 1,
        u"title": u"Buy groceries",
        u"description": u"Milk, Cheese, Pizza, Fruit, Tylenol",
        u"done": False
    },
    {
        u"id": 2,
        u"title": u"Learn Python",
        u"description": u"Need to find a good Python tutorial on the web",
        u"done": False
    }
]


@app.route(u"/todo/api/v1.0/tasks", methods=[u"GET"])

def get_tasks():
    return jsonify({u"tasks": tasks})


if __name__ == u"__main__":
    app.run(debug=True)
