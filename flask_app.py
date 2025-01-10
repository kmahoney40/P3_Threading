from threading import Lock
from flask import Flask, jsonify, request
import json
from werkzeug.serving import make_server

class FlaskApp:
    def __init__(self, e_stop_water_thread):
        self.app = Flask(__name__)
        self.lock = Lock()
        self.e_stop_water_thread = e_stop_water_thread

        @self.app.route('/', methods=['GET'])
        def index():
            with self.lock:
                self.e_stop_water_thread.set()
                return jsonify({"message": "Hello, World!"})

    def run(self):
        self.app.run(host='192.168.1.140', port=5000, debug=False)

# class FlaskApp:
#     def __init__(self, water_dict, new_water_dict_conf, e_stop_water_thread):
#         self.app = Flask(__name__)
#         self.configure_routes()
#         self.water_dict = water_dict
#         self.e_stop_water_thread = e_stop_water_thread
    
#     def configure_routes(self):
#         @self.app.route('/', methods=['GET'])   
#         def index(self):
#             self.e_stop_water_thread.set()
#             return 'Hello, World!'
#         #def index
        
#         @self.app.route('/another-endpoint', methods=['GET'])
#         def another_endpoint(self):
#             self.event_stop_water_thread.clear()
#             return 'WaterThread started. This is another endpoint.'
#         #def another_endpoint

#         @self.app.route('/runtimes', methods=['GET'])
#         def get_run_times(self):
#             return jsonify(self.water_dict['conf']['run_times'])
#         #def get_run_times
        
#         #KMDB Hmmm, stop water thread before this call!! Also, check with AI, create global new_run_times and call write_conf in main loop when new_run_times is set
#         @self.app.route('/update', methods=['POST'])
#         def update_run_times(self):
#             data = json.dumps(request.json)  # Use request.form for form data or request.data for raw data
#             if data is None:
#                 return jsonify({"error": "No JSON payload provided"})

#             # stop the water thread before updating the run times
#             self.e_stop_water_thread.set()
#             self.new_water_dict_conf[0] = data
            
#             # Process the data (example: log or return a response)
#             print(f"Received data: {data}")
#             return jsonify({"message": "Data received", "received_data": data})
#         # def update_run_times

#     def get_app(self):
#             return self.app
#     #def get_app