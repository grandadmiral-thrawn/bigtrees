#!/usr/bin/env python
"""
bigtrees web app

"""
from gevent import monkey
monkey.patch_all()

import os, platform, requests, json, datetime, time
from flask import Flask, session, request, escape, flash, url_for, redirect, render_template, g, send_from_directory
from flask.ext.socketio import SocketIO, emit

app = Flask(__name__)
app.secret_key = "lol hi"
socketio = SocketIO(app)

##########
# Routes #
##########

@app.route('/')
def index():
    return render_template('app.html')

def main():
    if platform.node() in ('vent',):
        app.debug = True
        socketio.run(app)
    else:
        app.debug = False
        socketio.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    main()
