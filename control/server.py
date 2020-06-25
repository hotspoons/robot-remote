from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit
from flask_classful import FlaskView, route
import time

class Server(Flask):
    _config = None
    state = None
    socketio = None
    last_timestamp = None
    connected = False
    
    def __init__(self, config):
        super().__init__(__name__)
        self._config = config
        self.config['EXPLAIN_TEMPLATE_LOADING'] = True
        self.config['SECRET_KEY'] = 'shhhhhh this is a secret'
        self.state = self._config.get_base_state()
        self.add_url_rule("/", "index", self.get_index)
        self.add_url_rule("/state", "state", self.put_state, methods=["PUT"])
        self.add_url_rule("/stream", "stream", self.get_stream_url, methods=["GET"])
        self.socketio = SocketIO(self, cors_allowed_origins='*')
        self.socketio.on_event("state", self.put_state)
        self.socketio.on_event("connect", self.connect)

    def start(self):
        self.socketio.run(self, host=self._config.address, port=self._config.port)

    def get_index(self):
        return render_template('index.html')
        
    def get_stream_url(self):
        return jsonify({"mjpeg_url": self._config.mjpeg_url, "h264_url": self._config.h264_url})
        
    def connect(self):
        emit('connected', {'data': True})
    
    """ Controller that accepts a "State" structure"""
    def put_state(self, json=None):
        self.last_timestamp = time.time()
        self.connected = True
        emit_event = False
        if json == None:
            new_state = request.get_json()
        else:
            new_state = json['data']
            emit_event = True
        state = self._config.get_base_state()
        for main_key in new_state:
            if main_key in state.keys():
                for key in new_state[main_key]:
                    if key in state[main_key].keys():
                        state[main_key][key] = new_state[main_key][key]
        self.state = state
        
        if emit_event == True:
            emit('state received', {'data': state})
        
        return jsonify(state)


    def get_state(self):
        if self.last_timestamp != None:
            if time.time() - self.last_timestamp > self._config.server_state_update_timeout:
                if self.connected == True:
                    print("It has been more than {} seconds since our last update from the client," + 
                          " returning to ground state".format(self._config.server_state_update_timeout))
                    self.connected = False
                return self._config.get_base_state()
        self.connected = True
        return self.state
