from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit
from flask_classful import FlaskView, route

""" TODO - Create an index page that serves a JavaScript client that
    connects over WebSockets, and the client uses a gamepad API like
    https://github.com/beejjorgensen/jsgamepad to emit the events. And
    maybe even try to bundle the MJPEG streamer with it! """
class Server(Flask):
    _config = None
    state = None
    socketio = None
    
    def __init__(self, config):
        super().__init__(__name__)
        self._config = config
        self.config['EXPLAIN_TEMPLATE_LOADING'] = True
        self.config['SECRET_KEY'] = 'shhhhhh this is a secret'
        self.state = self._config.get_base_state()
        self.add_url_rule("/", "index", self.get_index)
        self.add_url_rule("/state", "state", self.put_state, methods=["PUT"])
        self.socketio = SocketIO(self, cors_allowed_origins='*')
        self.socketio.on_event("state", self.put_state)
        self.socketio.on_event("connect", self.connect)

    def start(self):
        self.socketio.run(self, host=self._config.address, port=self._config.port)

    def get_index(self):
        return render_template('index.html')
        
    def connect(self):
        emit('connected', {'data': True})
    
    """ Controller that accepts a "State" structure"""
    def put_state(self, json=None):
        emit_event = False
        print(json)
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
        return self.state
