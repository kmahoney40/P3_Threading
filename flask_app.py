from threading import Lock
from flask import Flask, jsonify, request
import json
from werkzeug.serving import make_server

class FlaskApp:
    def __init__(self, logger, water_dict, new_water_dict_conf, e_stop_water_thread):
        self.app = Flask(__name__)
        self.server = None  # Placeholder for the make_server instance
        self.lock = Lock()
        self.ll = logger
        self.water_dict = water_dict
        self.new_water_dict_conf = new_water_dict_conf
        self.e_stop_water_thread = e_stop_water_thread
        self.ll.log("FlaskApp init " + str(self.app.url_map))
        
        @self.app.route('/', methods=['GET'])
        def index():
            with self.lock:
                self.e_stop_water_thread.set()
                return jsonify({"message": "Hello, World!"})
        #def index

        @self.app.route('/runtimes', methods=['GET'])
        def get_run_times():
            with self.lock:
                return jsonify(self.water_dict['conf']['run_times'])
        # def get_runtimes

        @self.app.route('/post_kmdb', methods=['POST'])
        def post_kmdb():
            with self.lock:
                return jsonify({"message": "Data received", "received_data": "update_runtimes"})
        #def post_kmdb
                
        @self.app.route('/update_runtimes', methods=['POST'])
        def update_run_times():
            try:
                with self.lock:
                    
                    data = json.dumps(request.json)

                    obj = json.loads(data)
                    self.ll.log("FlaskApp.update update_run_times data: " + str(data))
                    self.ll.log("FlaskApp.update update_run_times obj[1][3]: " + str(obj[1][3]))
                    self.ll.log("FlaskApp.update update_run_times obj[1][3]: " + str(obj[1]))

                    is_valid = self.validate_runtimes_json(obj)

                    if is_valid:
                        self.ll.log("FlaskApp.update update_run_times")
                        #print(f"FlaskApp.update update_run_times")
                        data = json.dumps(request.json)  # Use request.form for form data or request.data for raw data
                        #print(f"FlaskApp.update update_run_times: data: " + str(data))
                        self.ll.log("FlaskApp.update update_run_times: data: " + str(data))
                        if data is None:
                            return jsonify({"error": "No JSON payload provided"})

                        # stop the water thread before updating the run times
                        self.e_stop_water_thread.set()
                        self.new_water_dict_conf[0] = data
                        
                        # Process the data (example: log or return a response)
                        #print(f"Received data: {data}")
                        return jsonify({"message": "Data received", "received_data": data})
                    else:
                        return jsonify({"error": "Invalid JSON payload provided"})
            except Exception as e:
                self.ll.log(f"FlaskApp.update update_run_times: Exception: {str(e)}")
                print(f"FlaskApp.update update_run_times: Exception: {str(e)}")
                return jsonify({"error": "Exception occurred while updating run times: " + str(e)})
        # def update_run_times



    def run(self):
        #self.app.run(host='192.168.1.140', port=5000, debug=False)
        self.server = make_server('192.168.1.140', 5000, self.app)
        self.ctx = self.app.app_context()
        self.ctx.push()
        #print("Flask server starting with make_server...")
        self.server.serve_forever()

    def shutdown(self):
        """Gracefully shut down the server."""
        if self.server:
            print("Shutting down Flask server...")
            self.server.shutdown()
            
    def validate_runtimes_json(self, data):
        try:
            # Ensure it's a list
            if not isinstance(data, list) or len(data) != 8:
                return False

            # Validate each inner list
            for inner_list in data:
                if not isinstance(inner_list, list) or len(inner_list) != 8:
                    return False
                # Ensure all elements in the inner list are integers or floats
                if not all(isinstance(item, (int)) for item in inner_list):
                    return False
            return True
        except ValueError as e:
            self.ll.log(f"FlaskApp.validate_runtimes_json: Exception: {str(e)}")
            return False
            
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